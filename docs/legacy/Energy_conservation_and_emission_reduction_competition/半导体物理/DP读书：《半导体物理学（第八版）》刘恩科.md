# DP读书：《半导体物理学（第八版）》刘恩科

@[TOC](3min速通半导体物理之绪论)

# 绪论
## 第一章 半导体中的电子状态

### 1.1 半导体的晶格结构和结合性质

#### 1.1.1 金刚石型结构和共价键

* **金刚石型结构**：金刚石型结构是最简单的立方晶格结构，其中每个原子都与其他四个原子通过共价键结合。这种结构在硅和锗等半导体中很常见。
* **共价键**：在金刚石型结构中，原子之间通过共享电子形成共价键。这种键合方式使得电子在原子间移动而不容易被外部电场影响，从而形成了半导体的特性。


 ```mermaid 
graph TD  
    A["金刚石型结构"]  
    B["共价键"]  
  
    A --> B  
    A --> C["硅"]  
    A --> D["锗"]  
  
    B --> E["电子共享"]  
    B --> F["不易受外部电场影响"]  
    B --> G["形成半导体特性"]  
  
    style A fill:#f9f,stroke:#333,stroke-width:2px  
    style B fill:#ccf,stroke:#f66,stroke-width:2px  
    style C fill:#ccf,stroke:#6f6,stroke-width:2px  
    style D fill:#ccf,stroke:#6f6,stroke-width:2px  
    style E fill:#ccf,stroke:#6c6,stroke-width:2px  
    style F fill:#ccf,stroke:#6c6,stroke-width:2px  
    style G fill:#ccf,stroke:#6c6,stroke-width:2px
  ```



#### 1.1.2 闪锌矿型结构和混合键

* **闪锌矿型结构**：闪锌矿型结构是另一种常见的半导体结构，其中原子以四面体方式排列，但键合方式与金刚石型略有不同。
* **混合键**：在闪锌矿型结构中，原子之间的键合不再是纯粹的共价键，而是包含了一定的离子键和金属键成分，这使得电子状态更加复杂。


```mermaid 
graph TD  
    A["闪锌矿型结构"]  
    B["混合键"]  
  
    A --> B  
    A --> C["原子四面体排列"]  
    A --> D["键合方式与金刚石型不同"]  
  
    B --> E["包含离子键成分"]  
    B --> F["包含金属键成分"]  
    B --> G["电子状态更复杂"]  
  
    style A fill:#ccf,stroke:#f66,stroke-width:2px  
    style B fill:#ccf,stroke:#6f6,stroke-width:2px  
    style C fill:#ccf,stroke:#6c6,stroke-width:2px  
    style D fill:#ccf,stroke:#6c6,stroke-width:2px  
    style E fill:#ccf,stroke:#6c6,stroke-width:2px  
    style F fill:#ccf,stroke:#6c6,stroke-width:2px  
    style G fill:#ccf,stroke:#6c6,stroke-width:2px
  ```
  
#### 1.1.3 纤锌矿型结构

* **纤锌矿型结构**：纤锌矿型结构是另一种半导体结构，其特点是原子排列成六方密堆积，形成六边形晶格。
* **特性**：纤锌矿型结构中的原子间距较大，使得电子更容易受到外部电场的影响，从而影响了其电子状态和导电性质。

### 1.2 半导体中电子的状态和能带

#### 1.2.1 原子的能级和晶体的能带

* **原子的能级**：原子中的电子占据特定的能级，这些能级是分立的。
* **晶体的能带**：在晶体中，由于原子之间的相互作用，电子的能级会形成连续的能带。

#### 1.2.2 半导体中电子的状态和能带

* **半导体的能带结构**：半导体中的能带结构包括价带、导带和禁带。价带中的电子在室温下是填满的，而导带是空的。禁带是价带和导带之间的能量区域，其中的电子不易被激发。
* **电子的激发和跃迁**：当外部能量（如光照）作用于半导体时，价带中的电子可以被激发到导带，从而产生电流。

#### 1.2.3 导体、半导体、绝缘体的能带

* **导体的能带**：导体的能带结构中，导带与价带之间的禁带宽度很小，因此电子容易从价带跃迁到导带，形成良好的导电性能。
* **半导体的能带**：半导体的禁带宽度适中，需要在一定的外部能量作用下才能实现电子的跃迁和导电。
* **绝缘体的能带**：绝缘体的禁带宽度很大，电子很难从价带跃迁到导带，因此导电性能很差。
```mermaid 
graph TD  
    A["能带结构"]  
    B["导体"]  
    C["半导体"]  
    D["绝缘体"]  
  
    E["禁带宽度很小"]  
    F["禁带宽度适中"]  
    G["禁带宽度很大"]  
  
    H["电子容易跃迁"]  
    I["需要外部能量"]  
    J["电子难跃迁"]  
  
    K["良好导电性能"]  
    L["导电性能适中"]  
    M["导电性能很差"]  
  
    A --> B  
    A --> C  
    A --> D  
  
    B --> E  
    E --> H  
    H --> K  
  
    C --> F  
    F --> I  
  
    D --> G  
    G --> J  
    J --> M  
  
    style A fill:#ccf,stroke:#6f6,stroke-width:2px  
    style B fill:#ccf,stroke:#6c6,stroke-width:2px  
    style C fill:#ccf,stroke:#6c6,stroke-width:2px  
    style D fill:#ccf,stroke:#6c6,stroke-width:2px  
    style E fill:#ccf,stroke:#6c6,stroke-width:2px  
    style F fill:#ccf,stroke:#6c6,stroke-width:2px  
    style G fill:#ccf,stroke:#6c6,stroke-width:2px  
    style H fill:#ccf,stroke:#6c6,stroke-width:2px  
    style I fill:#ccf,stroke:#6c6,stroke-width:2px  
    style J fill:#ccf,stroke:#6c6,stroke-width:2px  
    style K fill:#ccf,stroke:#6c6,stroke-width:2px  
    style L fill:#ccf,stroke:#6c6,stroke-width:2px  
    style M fill:#ccf,stroke:#6c6,stroke-width:2px
  ```
  