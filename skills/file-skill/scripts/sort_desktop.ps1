<#
.SYNOPSIS
    Desktop icon auto-arrange and sort script (PowerShell, Windows)
.DESCRIPTION
    Uses the IFolderView2 COM interface to:
    1. Sort desktop icons by ItemType (the only supported sort mode)
    2. Enable "Auto Arrange Icons" to compact layout and eliminate gaps
    All without restarting Explorer.
.PARAMETER SortBy
    Sort column: only ItemType is supported
#>
param(
    [ValidateSet("ItemType")]
    [string]$SortBy = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ---------------------------------------------------------------------------
# Compile C# helper for IFolderView2 COM access
# ---------------------------------------------------------------------------
$csCode = @"
using System;
using System.Runtime.InteropServices;

public static class DesktopFolderView
{
    public const uint FWF_AUTOARRANGE = 0x00000001;
    public const uint FWF_SNAPTOGRID  = 0x00200000;

    // SORTDIRECTION enum
    public const int SORT_DESCENDING = -1;
    public const int SORT_ASCENDING  = 1;

    // PROPERTYKEY structure
    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    public struct PROPERTYKEY
    {
        public Guid fmtid;
        public uint pid;
    }

    // SORTCOLUMN structure
    [StructLayout(LayoutKind.Sequential, Pack = 4)]
    public struct SORTCOLUMN
    {
        public PROPERTYKEY propkey;
        public int direction;
    }

    // Well-known PROPERTYKEYs for sorting
    // System.ItemNameDisplay: {B725F130-47EF-101A-A5F1-02608C9EEBAC}, 10
    public static readonly PROPERTYKEY PKEY_ItemNameDisplay = new PROPERTYKEY {
        fmtid = new Guid("B725F130-47EF-101A-A5F1-02608C9EEBAC"), pid = 10
    };
    // System.Size: {B725F130-47EF-101A-A5F1-02608C9EEBAC}, 12
    public static readonly PROPERTYKEY PKEY_Size = new PROPERTYKEY {
        fmtid = new Guid("B725F130-47EF-101A-A5F1-02608C9EEBAC"), pid = 12
    };
    // System.ItemTypeText: {B725F130-47EF-101A-A5F1-02608C9EEBAC}, 4
    public static readonly PROPERTYKEY PKEY_ItemTypeText = new PROPERTYKEY {
        fmtid = new Guid("B725F130-47EF-101A-A5F1-02608C9EEBAC"), pid = 4
    };
    // System.DateModified: {B725F130-47EF-101A-A5F1-02608C9EEBAC}, 14
    public static readonly PROPERTYKEY PKEY_DateModified = new PROPERTYKEY {
        fmtid = new Guid("B725F130-47EF-101A-A5F1-02608C9EEBAC"), pid = 14
    };

    [ComImport, Guid("6D5140C1-7436-11CE-8034-00AA006009FA"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IServiceProvider
    {
        [PreserveSig]
        int QueryService(ref Guid guidService, ref Guid riid, out IntPtr ppvObject);
    }

    [ComImport, Guid("000214E2-0000-0000-C000-000000000046"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IShellBrowser
    {
        [PreserveSig] int GetWindow(out IntPtr phwnd);
        [PreserveSig] int ContextSensitiveHelp(bool f);
        [PreserveSig] int InsertMenusSB(IntPtr h, IntPtr l);
        [PreserveSig] int SetMenuSB(IntPtr h1, IntPtr h2, IntPtr h3);
        [PreserveSig] int RemoveMenusSB(IntPtr h);
        [PreserveSig] int SetStatusTextSB(IntPtr p);
        [PreserveSig] int EnableModelessSB(bool f);
        [PreserveSig] int TranslateAcceleratorSB(IntPtr p, ushort w);
        [PreserveSig] int BrowseObject(IntPtr pidl, uint flags);
        [PreserveSig] int GetViewStateStream(uint grfMode, out IntPtr ppStrm);
        [PreserveSig] int GetControlWindow(uint id, out IntPtr phwnd);
        [PreserveSig] int SendControlMsg(uint id, uint msg, IntPtr wp, IntPtr lp, out IntPtr ret);
        [PreserveSig] int QueryActiveShellView([MarshalAs(UnmanagedType.IUnknown)] out object ppshv);
    }

    // IFolderView2 with complete vtable in correct order
    // Inherits from IFolderView which has 14 methods after IUnknown
    [ComImport, Guid("1af3a467-214f-4298-908e-06b03e0b39f9"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IFolderView2
    {
        // === IFolderView methods (inherited, must be declared to maintain vtable order) ===
        [PreserveSig] int GetCurrentViewMode(out uint p);
        [PreserveSig] int SetCurrentViewMode(uint v);
        [PreserveSig] int GetFolder(ref Guid riid, [MarshalAs(UnmanagedType.IUnknown)] out object ppv);
        [PreserveSig] int Item(int i, out IntPtr ppidl);
        [PreserveSig] int ItemCount(uint f, out int c);
        [PreserveSig] int Items(uint f, ref Guid riid, [MarshalAs(UnmanagedType.IUnknown)] out object ppv);
        [PreserveSig] int GetSelectionMarkedItem(out int i);
        [PreserveSig] int GetFocusedItem(out int i);
        [PreserveSig] int GetItemPosition(IntPtr pidl, out long ppt);
        [PreserveSig] int GetSpacing(out long ppt);
        [PreserveSig] int GetDefaultSpacing(out long ppt);
        [PreserveSig] int GetAutoArrange();
        [PreserveSig] int SelectItem(int i, uint f);
        [PreserveSig] int SelectAndPositionItems(uint cidl, IntPtr apidl, IntPtr apt, uint f);

        // === IFolderView2 methods (in vtable order from shobjidl_core.h) ===
        [PreserveSig] int SetGroupBy(ref PROPERTYKEY key, [MarshalAs(UnmanagedType.Bool)] bool fAscending);
        [PreserveSig] int GetGroupBy(out PROPERTYKEY key, [MarshalAs(UnmanagedType.Bool)] out bool fAscending);

        [PreserveSig] int _SetViewProperty();       // placeholder
        [PreserveSig] int _GetViewProperty();       // placeholder
        [PreserveSig] int _SetTileViewProperties();  // placeholder
        [PreserveSig] int _SetExtendedTileViewProperties(); // placeholder
        [PreserveSig] int SetText(int t, [MarshalAs(UnmanagedType.LPWStr)] string p);

        [PreserveSig] int SetCurrentFolderFlags(uint dwMask, uint dwFlags);
        [PreserveSig] int GetCurrentFolderFlags(out uint pdwFlags);

        [PreserveSig] int GetSortColumnCount(out int pcColumns);
        [PreserveSig] int SetSortColumns([MarshalAs(UnmanagedType.LPArray)] SORTCOLUMN[] rgSortColumns, int cColumns);
        [PreserveSig] int GetSortColumns([MarshalAs(UnmanagedType.LPArray, SizeParamIndex = 1)] SORTCOLUMN[] rgSortColumns, int cColumns);
    }

    private static IFolderView2 GetDesktopFolderView()
    {
        Guid clsid = new Guid("9BA05972-F6A8-11CF-A442-00A0C90A8F39");
        Type swType = Type.GetTypeFromCLSID(clsid, true);
        object sw = Activator.CreateInstance(swType);

        object[] args = new object[] { 0, 0, 8, 0, 1 };
        object webBrowser = sw.GetType().InvokeMember("FindWindowSW",
            System.Reflection.BindingFlags.InvokeMethod, null, sw, args);
        if (webBrowser == null)
            throw new InvalidOperationException("FindWindowSW returned null - desktop shell not found");

        IServiceProvider sp = (IServiceProvider)webBrowser;
        Guid sidBrowser = new Guid("4C96BE40-915C-11CF-99D3-00AA004AE837");
        Guid iidBrowser = new Guid("000214E2-0000-0000-C000-000000000046");
        IntPtr pBrowser;
        int hr = sp.QueryService(ref sidBrowser, ref iidBrowser, out pBrowser);
        if (hr != 0 || pBrowser == IntPtr.Zero)
            throw new COMException("QueryService for IShellBrowser failed", hr);

        IShellBrowser browser = (IShellBrowser)Marshal.GetObjectForIUnknown(pBrowser);
        Marshal.Release(pBrowser);

        object shellView;
        hr = browser.QueryActiveShellView(out shellView);
        if (hr != 0 || shellView == null)
            throw new COMException("QueryActiveShellView failed", hr);

        Guid iidFV2 = new Guid("1af3a467-214f-4298-908e-06b03e0b39f9");
        IntPtr pUnk = Marshal.GetIUnknownForObject(shellView);
        IntPtr pFV2;
        hr = Marshal.QueryInterface(pUnk, ref iidFV2, out pFV2);
        Marshal.Release(pUnk);
        if (hr != 0 || pFV2 == IntPtr.Zero)
            throw new COMException("QueryInterface for IFolderView2 failed", hr);

        IFolderView2 fv2 = (IFolderView2)Marshal.GetObjectForIUnknown(pFV2);
        Marshal.Release(pFV2);
        return fv2;
    }

    public static uint GetCurrentFlags()
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        uint flags;
        fv2.GetCurrentFolderFlags(out flags);
        return flags;
    }

    public static bool IsAutoArrangeOn()
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        return fv2.GetAutoArrange() == 0;
    }

    public static int EnableAutoArrange()
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        uint mask = FWF_AUTOARRANGE | FWF_SNAPTOGRID;
        return fv2.SetCurrentFolderFlags(mask, mask);
    }

    public static int DisableAutoArrange()
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        return fv2.SetCurrentFolderFlags(FWF_AUTOARRANGE, 0);
    }

    public static int SetFlags(uint mask, uint flags)
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        return fv2.SetCurrentFolderFlags(mask, flags);
    }

    /// <summary>
    /// Sort desktop icons by ItemType (the only supported sort mode).
    /// </summary>
    public static int SortByColumn(string sortBy)
    {
        IFolderView2 fv2 = GetDesktopFolderView();

        SORTCOLUMN sc = new SORTCOLUMN();
        sc.direction = SORT_DESCENDING;
        sc.propkey = PKEY_ItemTypeText;

        SORTCOLUMN[] columns = new SORTCOLUMN[] { sc };
        return fv2.SetSortColumns(columns, 1);
    }

    /// <summary>
    /// Get current sort column info (for diagnostics).
    /// </summary>
    public static string GetCurrentSortInfo()
    {
        IFolderView2 fv2 = GetDesktopFolderView();
        int count;
        int hr = fv2.GetSortColumnCount(out count);
        if (hr != 0) return "GetSortColumnCount failed: HR=0x" + hr.ToString("X8");

        if (count <= 0) return "No sort columns set";

        SORTCOLUMN[] cols = new SORTCOLUMN[count];
        hr = fv2.GetSortColumns(cols, count);
        if (hr != 0) return "GetSortColumns failed: HR=0x" + hr.ToString("X8");

        string result = "";
        for (int i = 0; i < count; i++)
        {
            string dir = cols[i].direction > 0 ? "ASC" : "DESC";
            result += string.Format("Column[{0}]: fmtid={1}, pid={2}, dir={3}; ",
                i, cols[i].propkey.fmtid, cols[i].propkey.pid, dir);
        }
        return result;
    }
}
"@

try {
    Add-Type -TypeDefinition $csCode
} catch {
    $result = @{
        status  = "error"
        message = "Failed to compile COM helper: $($_.Exception.Message)"
    }
    $result | ConvertTo-Json -Depth 5
    exit 1
}

# ---------------------------------------------------------------------------
# Main Logic
# ---------------------------------------------------------------------------
$methodsTried = @()

try {
    # Read current state
    $wasAutoArrange = [DesktopFolderView]::IsAutoArrangeOn()
    $originalFlags = [DesktopFolderView]::GetCurrentFlags()
    $methodsTried += "Current state: flags=0x$($originalFlags.ToString('X8')), autoArrange=$wasAutoArrange"

    # Step 1: Sort by column if requested
    if ($SortBy -ne "") {
        $sortInfo = [DesktopFolderView]::GetCurrentSortInfo()
        $methodsTried += "Before sort: $sortInfo"

        $hrSort = [DesktopFolderView]::SortByColumn($SortBy)
        $methodsTried += "SetSortColumns('$SortBy') HR=0x$($hrSort.ToString('X8'))"

        Start-Sleep -Milliseconds 500

        $sortInfoAfter = [DesktopFolderView]::GetCurrentSortInfo()
        $methodsTried += "After sort: $sortInfoAfter"
    }

    # Step 2: Auto-arrange to compact icons
    if ($wasAutoArrange) {
        $hr1 = [DesktopFolderView]::DisableAutoArrange()
        $methodsTried += "Disabled auto-arrange (HR=0x$($hr1.ToString('X8')))"
        Start-Sleep -Milliseconds 500

        $hr2 = [DesktopFolderView]::EnableAutoArrange()
        $methodsTried += "Re-enabled auto-arrange (HR=0x$($hr2.ToString('X8')))"
        Start-Sleep -Seconds 2
    } else {
        $hr1 = [DesktopFolderView]::EnableAutoArrange()
        $methodsTried += "Enabled auto-arrange (HR=0x$($hr1.ToString('X8')))"
        Start-Sleep -Seconds 2

        $hr2 = [DesktopFolderView]::DisableAutoArrange()
        $methodsTried += "Restored auto-arrange OFF (HR=0x$($hr2.ToString('X8')))"
    }

    $result = @{
        status        = "success"
        platform      = "Windows"
        sort_by       = if ($SortBy -ne "") { $SortBy } else { "(no change)" }
        methods_tried = $methodsTried
        note          = "Desktop icons sorted and compacted via IFolderView2 COM interface (no Explorer restart)"
    }
} catch {
    $result = @{
        status        = "error"
        platform      = "Windows"
        methods_tried = $methodsTried
        message       = "Error: $($_.Exception.Message)"
    }
}

$result | ConvertTo-Json -Depth 5
