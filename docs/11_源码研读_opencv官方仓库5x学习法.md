# 11 · 源码研读：用本地 opencv-5.x 仓库学 OpenCV-Python

> 来源：本轮 Q&A 沉淀；配套 `00`–`10` 号手册与 `../机器视觉学习路线图.md`（v1.0，48 周）
> 本地仓库：`E:\Proj\pythonProject\opencv-5.x`（OpenCV **5.x 分支源码快照**，无 `.git`）
> 本手册定位：**不新增学习计划**，只回答"这份源码怎么用来学"，挂接到已有的 W1–W48 节奏上。

---

> **怎么读本手册（30 秒）**
> - **它是什么**：回答「本地 opencv 源码怎么用起来学」的 Q&A 沉淀，**不新增学习计划**。今天只做 §7 的「今日 5 件事」即可。
> - **顺序**：§0 五条结论 → §1 仓库里有什么 → §2 绑定机制（最关键认知）→ §4 四层阅读法 → §5 `warpAffine` 样板井；§2 的证据链可跳过，不影响使用。
> - ⚠️ **本手册的行号是例外**：文中 `文件:行` 与 `:nnn` 指的是**本地源码仓库 `E:/Proj/pythonProject/opencv-5.x`** 的行号；全库其他手册的 `:nnn` 才指路线图行号。别翻错文件。
> - **术语**：`Doxygen`＝C++ 文档生成工具，`Sphinx`＝Python 文档构建器，`CV_EXPORTS_W`＝头文件里「导出到 Python」的标记宏，`gen2.py`/`hdr_parser.py`/`cv2.cpp`＝Python 绑定生成脚本（分工见 §2）。
> - **版本**：本地源码是 **5.1-dev**，你装的是 **5.0.0.93**；签名一律以本机 `cv2.<func>.__doc__` 为准（§3）。

## 0. 结论先行

| # | 结论 | 为什么 |
|---|---|---|
| 1 | **这个仓库不是"官方文档项目"，是 OpenCV 的 C++ 主仓库** | 文档源码只是 `doc/` 一个子目录，主体是 `modules/`（C++ 实现）、`samples/`（示例）、`cmake/`（构建） |
| 2 | **仓库里没有 `cv2` 的 Python 源码**，别去找 `def warpAffine` | Python 接口是编译期从 C++ 头文件自动生成的（见 §2 证据链）。这是自学者最容易撞的墙 |
| 3 | **正确用法：官网渲染页当课本，本地仓库当"可运行的答案 + 词典 + 实验室"** | 仓库里的 `.markdown` 是 Doxygen（C++ 文档生成工具）方言，直接读会看到 `@subpage`、`@code{.py}`、`\f[...\f]` 等怪符号 |
| 4 | **版本口径必须先对齐：本地源码 5.1-dev ≠ 已装 5.0.0.93 ≠ 路线图 4.x** | 上一轮曾推测「源码 `warpAffine` 的 `hint` 参数你机器上可能没有」，**实测已证伪**：5.0.0 也有 `hint`。真正差异是 DNN 引擎常量名（见 §3） |
| 5 | **不要从 README 顺读，按"一个函数打一口井"纵向读** | 从教程 → 示例 → 头文件 → 实现/测试，四层各回答一类问题（见 §4） |

一句话：**把仓库当词典和实验室，不要当小说。**

---

## 1. 先认清这份本地仓库里有什么

根目录：`E:\Proj\pythonProject\opencv-5.x`

| 资产 | 本地路径（相对仓库根） | 用途 | 优先级 |
|---|---|---|---|
| Python 教程**正文源码** | `doc\py_tutorials\` | 官网 Python Tutorials 的原始 markdown，按 `py_gui / py_core / py_imgproc / py_features / py_calib3d / py_video / py_ml / py_photo / py_objdetect / py_bindings / py_setup` 分章 | ★★★ |
| 教程配套**可运行示例** | `samples\python\tutorial_code\` | 15 个子目录（`imgProc / ImgTrans / core / features / dnn / video / …`），每个都是最小 demo | ★★★ |
| **官方测试图片**（意外之喜） | `samples\data\` | `lena.jpg`、`messi5.jpg`、`sudoku.png`、`chessboard.png`、`chicky_512.png` 等都在本地，教程代码可以直接跑 | ★★★ |
| **API 契约**（权威签名 + 公式） | `modules\<模块>\include\opencv2\*.hpp` | 参数含义、默认值、前置条件、数学公式，比任何博客准 | ★★★ |
| **实现** | `modules\<模块>\src\*.cpp` | 算法细节、分支、加速路径 | ★★（选读） |
| **测试**（行为边界清单） | `modules\<模块>\test\test_*.cpp`、`modules\python\test\test_*.py` | 官方认定的"什么该报错、什么该兼容"，最适合做破坏性实验的题库 | ★★ |
| 绑定生成器 | `modules\python\src2\gen2.py`、`hdr_parser.py`、`cv2.cpp` | 解释"Python 接口从哪来"：`gen2.py` 生成包装代码、`hdr_parser.py` 解析 C++ 头文件、`cv2.cpp` 手写 Mat↔ndarray 转换 | ★（读一次即可） |
| 5.x 新文档工程 | `docs_sphinx\`（`conf.py`、`index_intro.md`、`requirements.txt`） | OpenCV 5 改用 Sphinx 构建文档，官网新结构由此而来 | ★ |
| C++ 教程源码 | `doc\tutorials\`、`doc\js_tutorials\` | 进阶 / 对照用 | ★ |

**明确跳过**（学了没收益）：`3rdparty\`、`cmake\`、`platforms\`、`hal\`、`apps\`、`modules\java\`、`modules\js\`、`modules\objc\`、`modules\ts\`、`modules\world\`、`include\`（只是汇总头）。

**5.x 结构变化**（判断版本的依据）：`modules\` 下 `calib3d` 已被拆成 `calib`、`geometry`、`stereo`、`ptcloud` 四个模块；`docs_sphinx\` 是 4.x 没有的。仓库 `README.md` 第 7 行指向 `https://docs.opencv.org/5.x/`，可确认这是 5.x 分支快照。

---

## 2. 最关键的一个认知：`cv2` 不是 Python 写的

### 证据链（全部来自你本地文件，可直接回查）

| 环节 | 文件:行（均相对 `E:/Proj/pythonProject/opencv-5.x`） | 原文要点 |
|---|---|---|
| 算法都在 C++ | `doc\py_tutorials\py_bindings\py_bindings_basics\py_bindings_basics.markdown:15-17` | "In OpenCV, all algorithms are implemented in C++… made possible by the bindings generators" |
| 包装层自动生成 | 同上 `:21-23` | "generates these wrapper functions automatically from the C++ headers using some Python scripts which are located in `modules/python/src2`" |
| 两个脚本的分工 | 同上 `:30-36` | `gen2.py` 是生成器，`hdr_parser.py` 把头文件拆成函数/枚举/类的 Python 列表 |
| 只有被标记的声明才导出 | 同上 `:38-43` | 开发者在函数前加宏，parser 只认这些 |
| 代码级证据 | `modules\python\src2\hdr_parser.py:573` | `if not (("CV_EXPORTS_AS" in decl_str) or ("CV_EXPORTS_W" in decl_str) or ("CV_WRAP" in decl_str)): return` |
| 宏替换 | `modules\python\src2\hdr_parser.py:441` | `("CV_EXPORTS_W", "")` 被批量剥离 |
| 一个真实例子 | `modules\imgproc\include\opencv2\imgproc.hpp:2165` | `CV_EXPORTS_W void warpAffine( InputArray src, OutputArray dst, … )` |
| NumPy ↔ cv::Mat | `py_bindings_basics.markdown:54-59` | ndarray 转成 `cv::Mat` → 调 C++ → 结果转回 ndarray，**运算几乎全在 C++** |
| 手工补充的包装 | `py_bindings_basics.markdown:47-52` | `Mat→ndarray`、`Size→tuple` 等手写包装在 `modules\python\src2\cv2.cpp` |

### 由此推出的三个"原来如此"

1. `help(cv2.warpAffine)` 很简略、参数是 C++ 顺序（src, dst→输出, M, dsize…）——因为签名是机器从 C++ 声明生成的。
2. 图像在 Python 里是 `numpy.ndarray`，但一进函数就变 `cv::Mat`；所以**性能优化方向是减少调用次数、用 ROI/向量化**，而不是优化 Python 循环。
3. `pip install opencv-python` 那个仓库只是**打包脚本**（打 wheel），不是学习材料；真正的知识全在你手上这份 `modules\` 里。

> **给 Java 背景的类比**：
> `CV_EXPORTS_W` ≈ 自定义注解 `@ExportToPython`；
> `hdr_parser.py + gen2.py` ≈ 编译期注解处理器，扫描源码生成 JNI/桥接层；
> 生成的 `pyopencv_generated_*.h` ≈ 自动生成的胶水代码；
> `cv2.pyd`（Windows 上是个 DLL）≈ 最终产物 `.jar/.dll`。
> 所以你在 Python 里看到的每个 `cv2.xxx`，都是**一份 C++ 声明的投影**，不是独立实现。

---

## 3. 动手前必做：三处版本对齐

| 口径 | 当前值 | 依据 |
|---|---|---|
| 本地源码 | **5.1-dev（5.x 分支快照）** | `README.md:7` → `docs.opencv.org/5.x/`；`docs_sphinx/conf.py:27` 为 `release = "5.1"`；`modules\` 有 `geometry/calib/stereo/ptcloud` 拆分 |
| 官网渲染文档 | **5.0**（新版 URL 结构） | `https://docs.opencv.org/5.0/py_tutorials/py_tutorials.html`；首页 `https://docs.opencv.org/5.0/` |
| 你机器上的 cv2 | **opencv-python 5.0.0.93**（conda `industrial_vision`，Python 3.11.17，NumPy 2.4.6，无 GPU） | 实测 `cv2.__version__`；系统默认 `python` 无 cv2，**必须先进 conda 环境** |
| 路线图 | **原按 4.x 写，2026-11-11 已对齐 5.0** | `机器视觉学习路线图.md:7`（头部注明"初版按 4.13 写，现已按 5.0.0.93 对齐"）、`:864-866`（已换 `docs.opencv.org/5.0/` 等）；`.md` 与 `.docx` 已同步 |

**已实测修正（2026-11-11）**：上一版曾推测 `imgproc.hpp:2170` 的 `hint` 参数可能不在 5.0.0 里，**这是错的**。本机实测 `cv2.warpAffine.__doc__` 第一行就是
`warpAffine(src, M, dsize[, dst[, flags[, borderMode[, borderValue[, hint]]]]]) -> dst`，
说明 `hint` 在 5.0.0 中确实存在。真正已验证的版本差异是：本地源码是 **5.1-dev**，DNN 引擎常量在开发版叫 `ENGINE_OPENCV`，而 5.0.0 实测为 `['ENGINE_AUTO', 'ENGINE_CLASSIC', 'ENGINE_NEW', 'ENGINE_ORT']`。详细对比见 `12_版本决策_4x与5x差异及路线调整.md`。

**但硬规则依然成立：**

```
函数签名以「本机 cv2.__doc__」为准，源码只用来回答「为什么」。
```

在 conda 环境里执行（自行运行，AI 不代跑 git/构建）：

```bash
conda activate industrial_vision
python -c "import cv2; print(cv2.__version__); print(cv2.warpAffine.__doc__)"
```

对照 `imgproc.hpp:2165-2170`，凡是 `__doc__` 里没有的参数，一律先不用。同时建议把路线图 `§9.1` 的两条 4.x 链接补上 5.0 版本（本手册不改动原文件，留给你自己决定）。

---

## 4. 核心方法：四层阅读法

不要按目录顺序读仓库。**每学一个 API，就纵向打一口井**：

| 层 | 读什么（本地路径） | 回答什么问题 | 产出 |
|---|---|---|---|
| **L1 教程** | 官网渲染页为主，`doc\py_tutorials\...\*.markdown` 原文为辅 | 这函数解决什么问题？典型组合是什么？ | 一张原理图 / 一句话用途 |
| **L2 示例** | `samples\python\tutorial_code\...\*.py` + `samples\data\` 的图 | 怎么跑起来？输入输出长什么样？ | 跑通 + 换成自己拍的图再跑一遍 |
| **L3 契约** | `modules\<模块>\include\opencv2\*.hpp` 里带 `CV_EXPORTS_W` 的声明及其上方注释 | 每个参数/枚举/默认值/公式/前置条件是什么？ | 参数表 + 三条"参数改了会怎样" |
| **L4 实现与测试** | `modules\<模块>\src\*.cpp`、`modules\<模块>\test\test_*.cpp` | 内部怎么算？边界和异常有哪些？ | 2–3 个故意失败的实验记录 |

**每层都配一次"破坏性实验"**（沿用 `00` 号手册 §0 三条硬规则、§7.1 破坏性实验表）：改一个参数、换一张图、故意传错类型，把现象记进 `docs/failures.md`。**抄通不算会，能解释失败才算会。**

> 为什么必须读 L3？因为官网 Python 教程是"教用法"的，很多约束只在 C++ 头文件的注释里写。例如下一节那个 `(width, height)` 陷阱，教程里只有一句 warning，头文件里才给出完整的 `dsize` 语义。

---

## 5. 立刻可做的样板：`warpAffine`（对接 `06` 号手册 §3 / W5 / S-29、S-30、S-32）

选它做第一口井，是因为它正好压在你当前的几何变换学习上，而且四层材料在本地全都齐。

### L1 · 教程

`doc\py_tutorials\py_imgproc\py_geometric_transformations\py_geometric_transformations.markdown`

- `:14-16`：`warpAffine` 吃 2×3 矩阵，`warpPerspective` 吃 3×3 矩阵
- `:40-49` / `:57-58`：平移矩阵 `M = [[1,0,tx],[0,1,ty]]`，必须 `np.float32`
- `:64-68`（**重点**）：第三个参数是输出尺寸 `(width, height)`，width 是列数、height 是行数
- `:74-99`：旋转用 `getRotationMatrix2D`，不要自己推矩阵
- `:104-122`：三点定仿射 `getAffineTransform`
- `:132-156`：四点定透视 `getPerspectiveTransform`

### L2 · 可运行示例

`samples\python\tutorial_code\ImgTrans\warp_affine\Geometric_Transforms_Demo.py`

- `:11`：`cv.samples.findFile(args.input)`，默认 `lena.jpg`
- `:18-23`：三点 → `getAffineTransform`
- `:27`：`warpAffine(src, warp_mat, (cols, rows))`
- `:39-43`：再叠一次 `getRotationMatrix2D` + `warpAffine`

跑法（图片就在本地，不用联网）：

```bash
conda activate industrial_vision
set OPENCV_SAMPLES_DATA_PATH=E:\Proj\pythonProject\opencv-5.x\samples\data
python "E:\Proj\pythonProject\opencv-5.x\samples\python\tutorial_code\ImgTrans\warp_affine\Geometric_Transforms_Demo.py" --input lena.jpg
```

或更省事：`--input E:\Proj\pythonProject\opencv-5.x\samples\data\chicky_512.png`（直接给绝对路径，绕开 `findFile` 的搜索路径）。已核实 `samples\data\` 里 `lena.jpg`、`messi5.jpg`、`sudoku.png` 均存在；`drawing.png` 不在，教程里用到它时换成别的图即可。

### L3 · API 契约

`modules\imgproc\include\opencv2\imgproc.hpp:2141-2170`

- `:2141-2147`：**逆映射公式** `dst(x,y) = src(M11·x + M12·y + M13, …)`；只有设了 `WARP_INVERSE_MAP` 才直接用 M，否则函数会先用 `invertAffineTransform` 求逆；**不能原地操作**
- `:2149-2161`：逐参数说明（`dsize`、`flags` 是插值方法与 `WARP_INVERSE_MAP` 的组合、`borderMode=BORDER_TRANSPARENT` 的语义、`hint`）
- `:2163`：`@sa` 给出相关函数族 `warpPerspective / resize / remap / getRectSubPix / transform`

这一层能回答教程没讲透的三个问题：为什么变换看起来"方向是反的"（内部做了求逆）、为什么 `flags` 能同时塞插值标志和 `WARP_INVERSE_MAP`（位或组合）、为什么传 `BORDER_TRANSPARENT` 时目标图要提前初始化。

### L4 · 实现与测试

- `modules\imgproc\src\imgwarp.cpp:2485-2535`：`cv::warpAffine` 入口。`:2495` 拒绝 N-D 输入；`:2501-2508` 走 OpenCL 分支；`:2514-2515` 检测到 src/dst 同内存就 `clone()`（对应"不能原地"）；`:2519-2520` **`INTER_AREA` 被悄悄降级为 `INTER_LINEAR`**；`:2522` 强制 M 必须是 2×3 且 `CV_32F/CV_64F`；`:2525-2535` 手写 2×3 矩阵求逆
- `modules\imgproc\test\test_imgwarp.cpp:925`（多通道）、`:1177-1186`（`reject_nd_input`：`EXPECT_THROW(warpAffine(...), cv::Exception)`）——官方给的边界题库

### 三个破坏性实验（做完这口井才算通）

| 改什么 | 预期 | 对应源码 |
|---|---|---|
| M 用 `np.float64` 或 `int` 数组 | 观察是否报错 / 结果是否一致 | `imgwarp.cpp:2522-2523` |
| `dsize` 写成 `(rows, cols)`（宽高对调） | 出图被裁切或变形，理解为什么是 `(w,h)` | 教程 `:64-68`、`imgwarp.cpp:2511` |
| 加上 `flags=cv.INTER_LINEAR \| cv.WARP_INVERSE_MAP` | 变换方向反转，直观看到"内部求逆"这一步 | `imgproc.hpp:2145-2147`、`imgwarp.cpp:2525` |

---

## 6. 挂接到你已有的 48 周路线（不另起炉灶）

| 已有周次 | 本地仓库对应目录 | 配套手册 |
|---|---|---|
| W1–W2（像素/阈值/滤波/形态学） | `doc\py_tutorials\py_gui\`、`py_core\`、`py_imgproc\` 下的 colorspaces / thresholding / filtering / morphological_ops；示例 `samples\python\tutorial_code\imgProc\` 下的 `threshold*` / `erosion_dilatation` / `Smoothing` | `04` |
| W3–W4（边缘/轮廓/模板/特征） | `py_imgproc\` 下的 gradients / canny / contours / template_matching、`py_features\`；示例 `ImgTrans\canny_detector`、`features\` | `05` |
| W5–W8（标定/几何变换/测量 P2） | `py_imgproc\py_geometric_transformations`、`py_calib3d\`；示例 `ImgTrans\warp_affine` / `remap`、`samples\python\calibrate.py` | `06` |
| W9–W20（打光/缺陷/定位） | `py_imgproc\` 下的 houghlines / houghcircles / watershed；`modules\imgproc\test` 做边界实验 | `07` |
| W21–W32（DL 部署） | `samples\python\tutorial_code\dnn\`、`modules\dnn\`（注意 §3 的引擎名版本差异） | `08` |
| W33+（工程化） | 看 `modules\python\src2\` 与 `modules\core\` 的**工程组织方式**，而不是算法 | `09` |

**每周只加一件事**：为每个新 API 填一张下面的卡片，累计进 `docs\`（沿用 `00` 号手册 `:83-86` 的"学 / 写 / 破 / 记"节奏）。不额外增加学习时长，不新开计划。

### 四层阅读卡模板（复制用）

```
## API：cv2.______
- L1 用途 / 典型组合：
- L2 可运行示例路径：            换成自己的图后现象：
- L3 签名（以本机 __doc__ 为准）：
  源码契约位置：xxx.hpp:____
  关键参数 / 默认值 / 数学公式：
- L4 实现位置：xxx.cpp:____     测试位置：test_xxx.cpp:____
  源码里发现的一条"文档没写"的行为：
- 破坏性实验 1/2/3：改了什么 → 现象 → 原因
- 与 Java/C# 的类比：
- 挂接编号：W__（周次） / S-__（知识点） / T_-__（动手任务，格式如 T1-19；三者释义见 `02` §1）
```

---

## 7. 使用这份本地仓库的 8 个坑

1. **没有 `.git`**：这是源码压缩包，不是克隆仓库。不能 `git log` / `git blame` / 切 tag；想看某行为何时引入，去 GitHub 网页看 history。**不影响读源码和跑示例**。
2. **`.markdown` 是 Doxygen（C++ 文档生成工具）方言**：`@subpage`、`@code{.py}`、`\f[…\f]`、`@sa` 在 VS Code 预览里是乱码感的符号。主读官网渲染页，本地原文只用来查代码段和链接。
3. **示例默认图靠 `cv.samples.findFile()`**：不设 `OPENCV_SAMPLES_DATA_PATH` 或不给绝对路径就会 "Could not open or find the image"。
4. **别试图完整编译**：需要 CMake + C++17 + 一堆第三方依赖，你无 GPU，学习阶段收益为负。你的 `cv2` 已经是编译好的成品。
5. **别按字母顺序读目录**：`3rdparty / cmake / hal / apps / platforms` 与学习 OpenCV-Python 无关。
6. **`opencv-python`（PyPI 打包仓库）不用下**：只有打包脚本，没有教程也没有算法。
7. **缺的两块按需再补**：`opencv_contrib`（`ml`、Haar、HOG 等扩展模块；**5.0 主包已自带 SIFT / ArUco 等常用项，不再需要为它们装 contrib**，见 `12` §3）、`opencv_extra`（大规模测试数据）。你本地的 `samples\data\` 已够 W1–W8 用。
8. **4.x 与 5.x 差异会影响搜索**：`calib3d` 拆成四个模块、文档 URL 从 `/4.x/d6/d00/tutorial_py_root.html` 变成 `/5.0/py_tutorials/py_tutorials.html`、DNN 引擎常量改名。搜到 4.x 教程时先确认版本，别混着抄。

---

## 8. 今天就做的 5 件事

1. 在 conda `industrial_vision` 里打印 `cv2.__version__` 和 `cv2.warpAffine.__doc__`，和 `imgproc.hpp:2165-2170` 逐项对照，记下差异。
2. 收藏 `https://docs.opencv.org/5.0/py_tutorials/py_tutorials.html`，作为 L1 主入口。
3. 用本地 `samples\data\lena.jpg` 跑通 `Geometric_Transforms_Demo.py`（`--input` 给绝对路径最省事）。
4. 读 `imgproc.hpp:2141-2163`，用自己的话解释"逆映射"和 `dsize=(w,h)`。
5. 做 §5 的三个破坏性实验，填一张四层阅读卡，存进 `docs\`。

> 判断标准（沿用 `00` 号手册 `:88`）：**能否在 2 分钟内讲清"这个函数干什么、参数为什么这么设计、我把它改坏后看到了什么"**。讲不清，就回 L3 再读一遍头文件。

---

*本手册基于本地仓库 `E:\Proj\pythonProject\opencv-5.x` 实际目录与文件行号核实，2026-11。源文件行号随 5.x 分支更新可能漂移，以关键词 `CV_EXPORTS_W void warpAffine`、`void cv::warpAffine` 重新定位即可。*
