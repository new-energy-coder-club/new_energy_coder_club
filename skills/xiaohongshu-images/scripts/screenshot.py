#!/usr/bin/env python3
"""
Screenshot Capture Script for Xiaohongshu Images

Captures sequential screenshots of the container element at precise 3:4 aspect ratio.
Ensures no text is cut off - if a line would be split, the current screenshot ends
at the previous line with whitespace padding, and the next screenshot starts from
that same line.

Usage:
    python screenshot.py <html_file_path>

Output:
    Screenshots saved to <html_folder>/_attachments/xhs-01.png, xhs-02.png, etc.
"""

import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is not installed.")
    print("Install it with: pip install playwright && playwright install chromium")
    sys.exit(1)


# Container dimensions (3:4 ratio)
CONTAINER_WIDTH = 600
CONTAINER_HEIGHT = 800
DEVICE_SCALE_FACTOR = 2

# Output dimensions (actual pixel size of screenshots)
OUTPUT_WIDTH = CONTAINER_WIDTH * DEVICE_SCALE_FACTOR   # 1200px
OUTPUT_HEIGHT = CONTAINER_HEIGHT * DEVICE_SCALE_FACTOR  # 1600px


def get_container_info(page) -> dict:
    """
    Get information about the container element.

    Returns:
        Dict with container's scroll info and dimensions
    """
    script = """
    () => {
        const container = document.querySelector('.container');
        if (!container) return null;

        const rect = container.getBoundingClientRect();
        return {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            scrollHeight: container.scrollHeight,
            clientHeight: container.clientHeight
        };
    }
    """
    return page.evaluate(script)


def scroll_container(page, scroll_top: int) -> int:
    """
    Scroll the container to a specific position.

    Returns:
        Actual scroll position after scrolling
    """
    script = f"""
    () => {{
        const container = document.querySelector('.container');
        if (container) {{
            container.scrollTop = {scroll_top};
            return container.scrollTop;
        }}
        return 0;
    }}
    """
    return page.evaluate(script)


def find_safe_cut_position(page, viewport_height: int) -> dict:
    """
    Find where to safely cut the current viewport without splitting text.

    Analyzes elements visible in the current viewport and finds the last
    complete element that fits entirely within the viewport.

    Args:
        page: Playwright page object
        viewport_height: Height of the visible area (container clientHeight)

    Returns:
        Dict with:
        - safe_y: Y position (relative to viewport top) where it's safe to cut
        - has_more: Whether there's more content below
        - next_start: Scroll position for the next screenshot
    """
    script = f"""
    () => {{
        const container = document.querySelector('.container');
        if (!container) return {{ safe_y: {viewport_height}, has_more: false, next_start: 0 }};

        const containerRect = container.getBoundingClientRect();
        const viewportHeight = {viewport_height};
        const currentScroll = container.scrollTop;
        const maxScroll = container.scrollHeight - container.clientHeight;

        // If we're at or past the end, no more content
        if (currentScroll >= maxScroll) {{
            return {{ safe_y: viewportHeight, has_more: false, next_start: currentScroll }};
        }}

        // Get all block-level elements that could be cut
        const blockElements = container.querySelectorAll(
            'p, h1, h2, h3, h4, h5, h6, li, blockquote, pre, div.content > *, img, figure'
        );

        let lastSafeY = 0;
        let nextStartScroll = currentScroll + viewportHeight;
        let foundCutElement = false;

        for (const el of blockElements) {{
            const rect = el.getBoundingClientRect();
            // Position relative to container's visible area
            const elTop = rect.top - containerRect.top;
            const elBottom = rect.bottom - containerRect.top;

            // Skip elements that are completely above the viewport
            if (elBottom <= 0) continue;

            // Skip elements that start below the viewport
            if (elTop >= viewportHeight) break;

            // Check if this element is fully visible in the viewport
            if (elTop >= 0 && elBottom <= viewportHeight) {{
                // Element fully visible - update safe cut point to its bottom
                lastSafeY = elBottom;
            }} else if (elTop >= 0 && elBottom > viewportHeight) {{
                // Element starts in viewport but extends beyond
                // Cut before this element
                foundCutElement = true;
                // Next screenshot should start with this element visible
                // We need to scroll so this element's top is at the viewport top
                nextStartScroll = currentScroll + elTop;
                break;
            }} else if (elTop < 0 && elBottom > viewportHeight) {{
                // Element spans the entire viewport (very tall element)
                // This is a special case - we'll include what we can
                lastSafeY = viewportHeight;
                nextStartScroll = currentScroll + viewportHeight;
                break;
            }}
        }}

        // If no cut element found, use full viewport
        if (!foundCutElement) {{
            lastSafeY = viewportHeight;
            nextStartScroll = currentScroll + viewportHeight;
        }}

        // Add small padding to avoid cutting too close to text
        if (lastSafeY < viewportHeight && lastSafeY > 0) {{
            lastSafeY = Math.min(lastSafeY + 5, viewportHeight);
        }}

        const hasMore = nextStartScroll < container.scrollHeight - 10;

        return {{
            safe_y: Math.floor(lastSafeY),
            has_more: hasMore,
            next_start: Math.floor(nextStartScroll)
        }};
    }}
    """
    return page.evaluate(script)


def add_whitespace_mask(page, from_y: int):
    """
    Add a whitespace mask to cover content below from_y position.

    This creates a div that covers the container from from_y to the bottom,
    matching the container's background color.
    """
    script = f"""
    () => {{
        const container = document.querySelector('.container');
        if (!container) return false;

        // Remove any existing mask
        const existingMask = document.getElementById('screenshot-mask');
        if (existingMask) existingMask.remove();

        // Get container's computed background color
        const bgColor = window.getComputedStyle(container).backgroundColor || '#F9F9F6';

        // Create mask element
        const mask = document.createElement('div');
        mask.id = 'screenshot-mask';
        mask.style.cssText = `
            position: absolute;
            left: 0;
            right: 0;
            top: {from_y}px;
            bottom: 0;
            background-color: #F9F9F6;
            z-index: 9999;
            pointer-events: none;
        `;

        // Ensure container has relative positioning
        const containerPosition = window.getComputedStyle(container).position;
        if (containerPosition === 'static') {{
            container.style.position = 'relative';
        }}

        container.appendChild(mask);
        return true;
    }}
    """
    return page.evaluate(script)


def remove_whitespace_mask(page):
    """Remove the whitespace mask."""
    script = """
    () => {
        const mask = document.getElementById('screenshot-mask');
        if (mask) {
            mask.remove();
            return true;
        }
        return false;
    }
    """
    return page.evaluate(script)


def capture_screenshots(html_path: Path, output_dir: Path):
    """
    Capture sequential 3:4 ratio screenshots of the container element.

    Args:
        html_path: Path to the HTML file
        output_dir: Directory to save screenshots
    """
    attachments_dir = output_dir / "_attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    print(f"Opening: {html_path}")
    print(f"Screenshots will be saved to: {attachments_dir}")
    print(f"Container size: {CONTAINER_WIDTH}x{CONTAINER_HEIGHT} (3:4 ratio)")
    print(f"Output size: {OUTPUT_WIDTH}x{OUTPUT_HEIGHT} ({DEVICE_SCALE_FACTOR}x scale)")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Viewport larger than container to ensure full visibility
        viewport_width = CONTAINER_WIDTH + 200
        viewport_height = CONTAINER_HEIGHT + 200

        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=DEVICE_SCALE_FACTOR
        )
        page = context.new_page()

        # Navigate and wait for content
        file_url = f"file://{html_path.resolve()}"
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(2000)  # Wait for fonts/images

        # Get container info
        container_info = get_container_info(page)
        if not container_info:
            print("Error: Could not find .container element")
            browser.close()
            return []

        print(f"Container dimensions: {container_info['width']}x{container_info['height']}")
        print(f"Content height: {container_info['scrollHeight']}px")
        print(f"Visible height: {container_info['clientHeight']}px")

        container = page.locator('.container')
        scroll_height = container_info['scrollHeight']
        client_height = container_info['clientHeight']

        # Start from the top
        scroll_container(page, 0)
        page.wait_for_timeout(100)

        screenshot_index = 1
        captured_screenshots = []
        current_scroll = 0
        max_iterations = 50  # Safety limit

        print(f"\nCapturing screenshots...")

        while screenshot_index <= max_iterations:
            # Scroll to current position
            actual_scroll = scroll_container(page, current_scroll)
            page.wait_for_timeout(150)

            # Find safe cut position
            cut_info = find_safe_cut_position(page, client_height)
            safe_y = cut_info['safe_y']
            has_more = cut_info['has_more']
            next_start = cut_info['next_start']

            # Add mask if we need to hide partial content
            needs_mask = safe_y < client_height and has_more
            if needs_mask:
                add_whitespace_mask(page, safe_y)
                page.wait_for_timeout(50)

            # Capture screenshot
            filename = f"xhs-{screenshot_index:02d}.png"
            filepath = attachments_dir / filename
            container.screenshot(path=str(filepath))

            # Remove mask
            if needs_mask:
                remove_whitespace_mask(page)

            visible_height = safe_y if needs_mask else client_height
            print(f"  {filename}: scroll={current_scroll}, visible={visible_height}px" +
                  (" [padded]" if needs_mask else ""))

            captured_screenshots.append(str(filepath))

            # Check if we're done
            if not has_more:
                break

            # Move to next section
            current_scroll = next_start
            screenshot_index += 1

            # Safety check - if we're not making progress
            if current_scroll >= scroll_height - 10:
                break

        browser.close()

    return captured_screenshots


def main():
    if len(sys.argv) < 2:
        print("Usage: python screenshot.py <html_file_path>")
        print()
        print("Captures sequential 3:4 ratio screenshots of the container element.")
        print("Features:")
        print("  - Precise 3:4 aspect ratio (600x800 -> 1200x1600 @2x)")
        print("  - Smart text boundary detection (no text cut-off)")
        print("  - Automatic whitespace padding when needed")
        print("  - Only captures container, excludes page background")
        sys.exit(1)

    html_path = Path(sys.argv[1]).resolve()

    if not html_path.exists():
        print(f"Error: File does not exist: {html_path}")
        sys.exit(1)

    if html_path.suffix.lower() not in ['.html', '.htm']:
        print(f"Warning: File does not appear to be HTML: {html_path}")

    output_dir = html_path.parent

    print("=" * 60)
    print("Xiaohongshu Screenshot Capture")
    print("=" * 60)

    try:
        screenshots = capture_screenshots(html_path, output_dir)

        print()
        print("=" * 60)
        print(f"Capture complete!")
        print(f"Total screenshots: {len(screenshots)}")
        print(f"Output location: {output_dir / '_attachments'}")
        print(f"Each screenshot: {OUTPUT_WIDTH}x{OUTPUT_HEIGHT}px (3:4 ratio)")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"Error during capture: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
