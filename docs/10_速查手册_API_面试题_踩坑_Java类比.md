# 10 · 速查手册：API / 面试题 / 踩坑 / Java 类比

> 用途：全程随手查、面试前突击、现场排错。来源：`../机器视觉学习路线图.md` `§4.2`（`:334-357`）、`§6`（`:636-725`）、`§7`（`:729-796`）、`§8`（`:813-838`）。
> 配套：[`00 总览`](./00_学习手册总览_路线与使用方法.md) · [`01 ToDoList`](./01_ToDoList拆解_48周动手任务清单.md) · [`02 ToStudyList`](./02_ToStudyList拆解_知识体系与自测清单.md) · 手册 `03`–`09`。

---

> **怎么读本手册（30 秒）**
> - **它是什么**：随手查 / 面试前突击 / 现场排错的速查表，**不是用来背的，也不是教材**。按 §0 的状态表直接跳到对应节，不要顺读。
> - **代号与行号**：`S-xx` / `T-xx` / `W` / `P0–P2` / `P1–P7` 见 [`02` §1 代号词典](./02_ToStudyList拆解_知识体系与自测清单.md)；全库 `:nnn` 一律指 `../机器视觉学习路线图.md` 的行号，**看不懂可跳过**。
> - **版本口径**：本手册 API 以本机 `cv2.__doc__` 为准；4.x 旧教程里的 contrib / 返回值说法按 `12` 号手册当兼容性阅读处理。

## 0. 一页纸使用说明

| 你现在的状态 | 翻到 |
|---|---|
| 写代码忘了函数签名 | §1 API 速查 + §1.9 最小脚本 |
| 报错看不懂 | §7 排错速查 |
| 面试前一晚 | §3 二十题标准回答 + §5 公式 |
| 参数怎么调都不对 | §2 二十个坑（多半是打光/标定问题） |
| Java 思维转不过来 | §4 对照表 |
| 忘了这周该做什么 | 回 `01` 号清单对应周 |

---

## 1. OpenCV API 速查（按工业使用频率，`:336-352`）

| 模块 | 函数 | 关键参数 / 易错点 |
|---|---|---|
| 基础 | `imread/imwrite/imshow` | BGR；中文路径用 `imencode/imdecode`；`imshow` 必须配 `waitKey` |
| 色彩 | `cvtColor` | `COLOR_BGR2GRAY` / `BGR2HSV` / `BGR2LAB`；matplotlib 显示要转 RGB |
| 通道 | `split/merge`、ROI 切片 | 切片是**视图**，要独立就 `.copy()` |
| 阈值 | `threshold` | 加 `THRESH_OTSU` 自动求阈值；暗目标用 `THRESH_BINARY_INV` |
| 阈值 | `adaptiveThreshold` | `blockSize` 必须奇数；光照不均首选 |
| 颜色 | `inRange` | HSV 的 H 范围 0–179；红色需两段合并 |
| 形态学 | `getStructuringElement` + `morphologyEx` | 核尺寸 ≈ 目标短边；开去噪、闭连线、顶帽提亮、黑帽提暗 |
| 滤波 | `GaussianBlur` / `medianBlur` / `bilateralFilter` | 核必须奇数；椒盐→中值、高斯→高斯、保边→双边（慢） |
| 边缘 | `Sobel` / `Canny` / `Laplacian` | Canny 前先高斯；双阈值比例 2:1~3:1 |
| 轮廓 | `findContours` | **统一写 `[-2]` 兼容 3.x/4.x/5.x**；`RETR_EXTERNAL` 只取外圈，`RETR_TREE` 保层级 |
| 轮廓 | `contourArea/arcLength/approxPolyDP/minAreaRect/boundingRect` | `minAreaRect` 角度随版本变化，用 `boxPoints` 自己算 |
| 连通域 | `connectedComponentsWithStats` | `stats[i]` = `[x,y,w,h,area]`；索引 0 是背景 |
| 几何 | `warpAffine/warpPerspective/getRotationMatrix2D/warpPolar` | 仿射 3 点、透视 4 点；`warpPolar` 拉直环形件 |
| 模板 | `matchTemplate` + `minMaxLoc` | `TM_CCOEFF_NORMED` 取最大值；`TM_SQDIFF*` 取最小值 |
| 特征 | `ORB_create/SIFT_create/BFMatcher/findHomography` | 5.0 主包自带 SIFT（旧教程「需 contrib」已过时，见 `12` §3）；`findHomography(..., cv2.RANSAC, 3.0)` |
| 标定 | `findChessboardCorners/cornerSubPix/calibrateCamera` | 15–30 张不同姿态；RMS < 0.5px |
| 校正 | `initUndistortRectifyMap` + `remap` | 实时视频预生成映射表，别每帧 `undistort` |
| 拟合 | `fitLine/fitEllipse/HoughLinesP/HoughCircles` | `fitEllipse` 至少 5 点；`DIST_HUBER` 抗离群 |
| 坐标 | `estimateAffine2D` / `transform` | 九点标定；看最大残差 < 0.1mm |
| 视频 | `VideoCapture/VideoWriter` | FPS 与算法 FPS 解耦；`Queue(maxsize=1)` 丢旧帧 |
| DNN | `dnn.readNetFromONNX` / `blobFromImage` | NCHW + RGB + 归一化，三样对齐 |
| 其他 | `LUT/equalizeHist/dft` | LUT 代替逐像素循环；dft 陷波去周期纹理 |

### 1.9 最小可运行脚本（复制即用）

```python
# cheat_sheet.py —— 12 行串起最常用的链路
import cv2
import numpy as np

img = np.full((240, 320, 3), 190, np.uint8)
cv2.circle(img, (160, 120), 30, 40, -1)                    # 暗"缺陷"
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
_, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, k)
n, labels, stats, cents = cv2.connectedComponentsWithStats(bw, 8)
cnts = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
edges = cv2.Canny(blur, 50, 150)
print("连通域:", n - 1, "轮廓:", len(cnts),
      "最大面积:", int(stats[1:, cv2.CC_STAT_AREA].max()) if n > 1 else 0,
      "边缘像素:", int((edges > 0).sum()))
```

**提速三件套（`:354-357`）**：① ROI 只处理关心区域；② 降采样粗定位再回原图精定位；③ `LUT` / `cv2.setNumThreads()` / 多进程。

---

## 2. 二十个坑：一页纸（`:729-796`）

### 认知类（1–8）

| # | 坑 | 对策 |
|---|---|---|
| 1 | 只看不写，收藏夹吃灰 | 每周有可运行产出，否则=没学 |
| 2 | 用"完美网图"练手 | 从第一天起用自己拍的图 |
| 3 | 迷信 DL、瞧不起传统 | 传统 1ms、可解释、免样本；能传统就传统 |
| 4 | 跳过打光直接调算法 | 先 2 小时调光，胜过 2 天调参 |
| 5 | 不做标定就谈精度 | 精度必须带标定 + GR&R |
| 6 | 炫技忽视节拍 CT | 先满足 100ms，再谈精度 |
| 7 | 只看漏检率 | 过杀高会被工人关掉 |
| 8 | 以为 OpenCV = 视觉 | 值钱的是选型、评估、现场、成本 |

### 技术类（9–16）

| # | 坑 | 对策 |
|---|---|---|
| 9 | 不学 C# | 项目 P7 必做，70% 现场软件是 C# |
| 10 | 不学 C++ | 看懂、能改、能调用即可 |
| 11 | 忽视光学/机械基础 | 景深、畸变、远心、安装刚度 |
| 12 | 不做工程化 | 参数外置、日志、异常、配置 |
| 13 | 不积累样本库 | 每项目存图、按类整理 |
| 14 | 不做性能优化 | numpy 向量化 / ROI / 降采样 / 多进程 |
| 15 | 不用版本管理 | 调参前先 commit，写清"改了什么、为什么" |
| 16 | 不写文档 | 每项目一页纸：目标/方案/参数/结果/坑 |

### 职业类（17–20）

| # | 坑 | 对策 |
|---|---|---|
| 17 | 不问"为什么" | 每个参数都要能解释 |
| 18 | 不与工艺/电气/机械沟通 | 视觉是系统的一部分 |
| 19 | 盲目报班 | 先自学 3 个月 |
| 20 | 不关注行业 | 选 1–2 个行业深耕 |

---

## 3. 二十道高频面试题：标准回答要点（`:815-836`）

> 每题控制在 2 分钟内；**先给结论，再补一个数字或场景**。

| # | 问题 | 回答要点 |
|---|---|---|
| 1 | 工业视觉有哪几类任务 | 定位 `(x,y,θ)`、测量 mm、检测 OK/NG、识别 字符串/类别 |
| 2 | 怎么按精度选相机 | `mm/px = FOV/像素数`；稳定精度取 3–5 像素；反推所需分辨率 |
| 3 | 镜头焦距怎么算 | `f = WD × 靶面 / FOV`，选接近的标准焦距；例题 300×7.2/100≈21.6mm |
| 4 | 景深受什么影响 | 光圈 F 数、放大倍率、允许弥散圆；**倍率越大景深越浅** |
| 5 | 远心镜头作用 | 无透视误差、畸变极小，尺寸测量首选；贵、需精密支架 |
| 6 | 全局 vs 卷帘快门 | 卷帘逐行曝光，运动物体果冻变形；飞拍必须全局快门 |
| 7 | 什么时候用背光 | 轮廓尺寸、缺料、孔位；黑白分明、边缘最锐利 |
| 8 | 同轴光解决什么 | 镜面/金属/玻璃反光，让表面划痕与细节可见 |
| 9 | 偏振片怎么用 | 镜头前 + 光源前各一片，消塑料/玻璃反光 |
| 10 | 相机标定原理 | 张正友：多姿态棋盘格 → 求内参 K + 畸变系数；重投影误差评价 |
| 11 | 重投影误差合格线 | **< 0.5 px**；> 1 px 多半是标定板不平、图像模糊、姿态不够 |
| 12 | 九点标定原理与误差 | 9 组对应点求 2×3 仿射；误差来自畸变、点位分布、机械重复定位、Z 高度变化 |
| 13 | eye-in-hand / eye-to-hand | 相机装末端（求相机↔法兰）/ 固定机架（求相机↔基座）；`calibrateHandEye` |
| 14 | 亚像素怎么实现 | 灰度插值/矩/`cornerSubPix`；或沿法线找梯度极值 + 抛物线插值 |
| 15 | 模板匹配原理与局限 | NCC 归一化互相关；怕旋转、缩放、光照、遮挡；替代：特征点单应性 / 形状匹配 |
| 16 | Canny 五步 | 高斯去噪 → 梯度幅值方向 → NMS → 双阈值 → 滞后连接 |
| 17 | Otsu 原理 | 遍历阈值，最大化类间方差 `w0·w1·(μ0−μ1)²`；双峰直方图最有效 |
| 18 | 开/闭运算作用 | 开=先腐后膨去亮噪点；闭=先膨后腐连断线填孔 |
| 19 | 传统缺陷检测方法 | Blob、黄金模板差分、顶帽/黑帽、频域陷波、光度立体、颜色统计 |
| 20 | 过杀率与漏检率权衡 | 此消彼长；产线更怕漏检（客诉召回），但过杀高会被弃用；**阈值是商务问题，写进验收标准** |

**加分题（`:838`）速记**：
- YOLO loss ≈ 分类损失 + 框回归（CIoU 完整交并比损失 / DFL 分布焦点损失）+ 置信度；anchor-free（无锚框）直接预测中心/边界偏移，省掉锚框超参。
- PatchCore 只用良品：建正常特征记忆库，推理看最近邻距离，因为 NG 样本稀少且形态不可枚举。
- ONNX 部署流程：训练 → 导出（固定/动态 batch、opset）→ ORT/OpenVINO/TensorRT → NCHW/RGB/归一化对齐 → 计时验收。
- 节拍优化顺序：ROI → 降采样 → LUT/向量化 → 多线程 → 硬件。
- 防呆：校验规则（格式/日期/MES 比对）、心跳超时判 NG、参数版本可回退。

---

## 4. Java → Python / C# 对照速查

| Java 习惯 | Python / OpenCV | C# / OpenCvSharp |
|---|---|---|
| `BufferedImage.getRGB(x,y)` | `img[y, x]`（**先行后列**） | `Mat.At<Vec3b>(y, x)` |
| `byte[]` 溢出回绕 | `uint8` 回绕；`cv2.add` 饱和 | `byte` 溢出回绕，需 `checked` 或 clamp |
| `Arrays.copyOfRange` | `arr[y1:y2, x1:x2].copy()` | `new Mat(mat, rect)` 注意释放 |
| `List<Handler>` + 策略模式 | `Pipeline` + `Detector` 插件（见 `09` §1.2） | `List<IDetector>` |
| `@ConfigurationProperties` / profile | `configs/*.yaml` + `load_cfg()` | `appsettings.json` |
| 订单状态枚举 + 迁移表 | `Enum` + `TRANSITIONS` 显式表（见 `09` §2） | 同左，`switch` 表达式 |
| `CompletableFuture` / 线程池 | `threading.Thread` + `queue.Queue` | `Task` / `Channel<T>` |
| Hystrix / Sentinel 超时熔断 | `socket.settimeout` + 重连 + 超时判 NG | `CancellationTokenSource` |
| 审计日志 + 附件表 | SQLite `inspection` 表 + NG 图路径 | EF Core + 文件表 |
| `try/finally` 释放连接 | `with` / `try...finally` | **`using` 释放 Mat，否则内存泄漏** |
| 单元测试 + 固定夹具 | `tests/run_regression.py` + `data/regression/` | xUnit + 固定图片集 |

> 集合/流对照：`list` ≈ `ArrayList`；`dict` ≈ `HashMap`；`np.ndarray` 向量化 ≈ `IntStream` 但**在 C 层批量执行**；生成器 ≈ `Stream` 惰性求值。
> 类型差异：Python 动态类型，靠 `shape/dtype` 自检；C# 泛型 `DenseTensor<float>` 形状必须和 ONNX 输入完全一致。

---

## 5. 公式速查（`:268-292`、`:324-328`、`:381-389`、`:450-453`）

```
镜头选型   f = WD × 靶面 / FOV
           β = 靶面 / FOV
           单像素精度 = FOV宽 / 水平像素数
           稳定测量精度 ≈ 3~5 像素 × 单像素精度
景深       DOF ≈ 2 · N · c · (1+β) / β²      (c ≈ 2×像元尺寸)
曝光上限   t ≤ 允许模糊量 / 运动速度        例 0.1mm / 200mm/s = 0.5ms
测量链路   图像 → 畸变校正 → 亚像素边缘 → 拟合 → 像素距离 × 像素当量 → mm
Otsu       σ²_between(t) = w0·w1·(μ0−μ1)²
九点标定   [X Y]ᵀ = M · [u v 1]ᵀ            M 为 2×3 仿射，残差 < 0.1mm
标定质量   重投影误差 < 0.5 px
漏检率     Escape  = FN / (TP+FN)            不良品被判 OK
过杀率     Overkill= FP / (FP+TN)            良品被判 NG
GR&R       同一工件测 30 次，标准差 ≤ 公差带 10%
工业指标   召回 > 99%，过杀 < 1%（以客户验收标准为准）
```

---

## 6. 命令速查

```bash
# 环境
conda activate industrial_vision
python -c "import cv2,numpy; print(cv2.__version__, numpy.__version__)"
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python==5.0.0.93 PySide6 pyyaml

# 训练 / 导出（无 GPU 用小配置）
pip install ultralytics onnxruntime anomalib
python src/algo/dl/yolo_demo.py
python src/algo/dl/export_infer.py

# 回归 / 压测
python tests/run_regression.py
python tests/stress_8h.py --seconds 60        # 先跑 60 秒，再跑 8 小时

# 参数版本（调参前必做）
git add -A && git commit -m "P3: min_area 50->80，因低角度打光后噪点变大"
```

---

## 7. 排错速查（报错 → 原因 → 处置）

| 现象 / 报错 | 最可能原因 | 处置 |
|---|---|---|
| `!_src.empty() in function 'cvtColor'` | `imread` 返回 None（路径/中文/格式） | 用 `imdecode(np.fromfile(...))`，见 `03` §3.4 |
| `AttributeError: module 'cv2' has no attribute 'SIFT_create'` | **5.0 主包自带 SIFT**；出现该报错多为装了 `headless` / 旧版包，或多包共存 | 先 `pip list` 确认只装一个 opencv 包且版本 5.0.0.93，再 `print(cv2.__file__)` 看实际导入路径；旧教程「重装 contrib」在 5.0 已不适用（`12` §3） |
| `findContours` 解包报错 | 3.x/4.x/5.x 返回值数量不同 | 统一 `cv2.findContours(...)[-2]` |
| `adaptiveThreshold` 断言失败 | `blockSize` 为偶数或 ≤1 | 取奇数 ≥3 |
| 阈值后一片白/一片黑 | 阈值方向反了 / 光照不均 | 换 `_INV`；改自适应阈值；**先查打光** |
| 检测框到处都是 | 差分前没对齐 / 开运算没做 | 特征对齐 + 形态学去噪 |
| 测量值整体偏 2% | 像素当量用理论值 | 标准件实测（`06` §4） |
| 视野边缘误差大 | 未畸变校正 / 标定板只拍中心 | 覆盖全视野重标 + `remap` |
| C# 与 Python 推理结果不一致 | NCHW / RGB / 归一化三样没对齐 | 逐项对照（`08` §6.2） |
| 运行几小时后内存上涨 | `Mat` 未释放 / 队列积压 / 日志无限存图 | `using`、`Queue(maxsize=1)`、日志轮转 |
| 界面假死、掉线不恢复 | 用 `sleep` 等 PLC 信号 | 状态机 + 超时 + 重连（`09` §2） |
| 算法 2 秒、节拍要求 100ms | 逐像素循环 / 全图处理 | ROI → 降采样 → LUT → 多线程 |

---

## 8. 回到执行

| 想做的事 | 打开 |
|---|---|
| 看这周该勾哪些任务 | [`01 ToDoList 拆解`](./01_ToDoList拆解_48周动手任务清单.md) |
| 给知识点打分、找薄弱项 | [`02 ToStudyList 拆解`](./02_ToStudyList拆解_知识体系与自测清单.md) |
| 按周系统学习 | [`03`](./03_学习手册_阶段0_环境与工具链.md) → [`04`](./04_学习手册_阶段1上_像素阈值滤波形态学.md) → [`05`](./05_学习手册_阶段1中_边缘轮廓模板匹配与特征.md) → [`06`](./06_学习手册_阶段1下_标定几何变换与尺寸测量P2.md) → [`07`](./07_学习手册_阶段2_成像打光缺陷检测与定位识别.md) → [`08`](./08_学习手册_阶段3_深度学习与部署.md) → [`09`](./09_学习手册_阶段4_系统集成与完整视觉软件.md) |
| 周复盘 / 季度回顾模板 | [`00 总览 §8`](./00_学习手册总览_路线与使用方法.md) |

> 最后一条：**这本速查手册不是用来背的，是用来"卡住时 30 秒内定位问题"的。** 真正的掌握来自 `01` 号清单里那些被勾掉的 `[x]`。


---

## 9. Q&A 补充 · `cap.read()` 的 `ret` 是什么（Q07 / 2026-11-12）

> **为什么放在末尾**：本节按 `13` 号 Q&A 规则追加。不插进 §1 API 速查表，是为了不挤偏本手册已有的行号引用（`docs/10:34/220` 等）。
> **路径约定（重要）**：本节形如 `videoio.hpp:1025`、`cap.cpp:551` 的行号，指的是**本地源码仓库** `E:/Proj/pythonProject/opencv-5.x`，不是路线图行号；全库裸 `:nnn` 才指 `../机器视觉学习路线图.md`。
> **实测环境**：conda `industrial_vision` → `opencv-python 5.0.0.93` / Python 3.11.17 / NumPy 2.4.6，无摄像头，用 `VideoWriter` 合成的临时 AVI 做可复现实验。

### 9.1 结论先行（30 秒）

`ret` 是 **return value** 的缩写，一个 `bool`。`cap.read()` 一次返回 **两个值**：

| 位置 | 习惯命名 | 类型 | 含义 |
|---|---|---|---|
| 第 1 个 | `ret` / `ok` / `success` | `bool` | 本次**是否真的拿到一帧非空图像** |
| 第 2 个 | `frame` | `np.ndarray` 或 `None` | 这一帧的 BGR 像素数组，形状 `(H, W, 3)`，`uint8` |

`ret, frame = cap.read()` 不是 OpenCV 专有语法，就是 **Python 的元组解包**：`read()` 返回 `(retval, image)`，证据是 `cv2.VideoCapture.read.__doc__` 首行 `read([, image]) -> retval, image`。

**一句话作用**：`ret` 是「这一帧能不能用」的开关。不检查它，视频读完或相机掉线的那一刻，程序就会把 `None` 传给 `cv2.cvtColor` 直接崩溃。

### 9.2 三个作用：为什么每个循环都要写 `if not ret: break`

| # | 场景 | `ret` 在管什么 | 不检查会怎样 |
|---|---|---|---|
| 1 | 视频文件读到末尾（EOF） | 循环的正常终止条件 | 无限循环处理 `None`，或抛出 `-215` 断言错误 |
| 2 | 工业相机断线 / 瞬时坏帧 | 采集链路的健康信号 | 缺陷检测静默跑空帧，可能漏检、误发 OK 信号给 PLC |
| 3 | 设备根本没打开 | 兜底：仍返回 `(False, None)`，**不抛异常** | 以为在采集，实际一帧没拿到，排查半天 |

官方标准写法见本地 `doc/py_tutorials/py_gui/py_video_display/py_video_display.markdown:33-38`：先 `isOpened()`，再 `ret, frame = cap.read()`，紧跟 `if not ret: break`，之后才做 `cvtColor` / `imshow`。

### 9.3 底层原理：`ret` 判的其实不是 `grab()` 成功

头文件注释（`videoio.hpp:1014-1025`）说得很直白：`read()` = `grab()` + `retrieve()` 的组合；返回 `false` 的两种典型原因是**相机已断开**或**文件里没有更多帧**，此时返回空图像。

关键在实现（`cap.cpp:551-561`）：

```cpp
bool VideoCapture::read(OutputArray image)
{
    CV_INSTRUMENT_REGION();
    if (grab())
    {
        retrieve(image);      // 注意：retrieve() 的返回值被丢弃了
    } else {
        image.release();
    }
    return !image.empty();    // ← ret 的真实来源
}
```

**推导一步一步来**：

1. `grab()` 只负责「从设备/解码器抢下一帧」，成功与否看 `cap.cpp:524-533`。
2. `retrieve()` 负责「解码并写进 `image`」，它自己也返回 `bool`（`cap.cpp:535-548`），但 `read()` **没接这个返回值**。
3. 所以 `read()` 最后返回的是 `!image.empty()` —— **判定对象是「最终图像是否非空」，不是「抓取动作是否成功」**。
4. 结论：日常把 `ret` 理解成「成功拿到一帧」没问题，但精确到源码，它是「拿到了一张非空图」。这也是多通道 / 特殊后端下可能出现 `grab=True` 却 `read=False` 的原因。

> 顺带对齐 `11` 号四层阅读法：这口井是「官网教程说 false → 头文件注释解释为什么 → 实现揭示真实判据」的典型例子，光看文档看不到第 3 步。

### 9.4 本机 5.0.0 实测（可复现）

用 `VideoWriter` 写 3 帧纯色 AVI，再连续读 6 次；另测不存在的摄像头 `VideoCapture(9999)`。

| # | 场景 | `ret` | `frame` |
|---|---|---|---|
| 1 | 读第 1–3 帧 | `True` | `ndarray(48, 64, 3)`，均值 0 / 60 / 120 |
| 2 | 第 4 次（EOF） | `False` | **`None`** |
| 3 | 继续读第 5、6 次 | `False` | `None`（不会自动重绕） |
| 4 | 设备不存在，`isOpened()=False` | `False` | `None`，**不抛异常** |
| 5 | 拿到 `frame=None` 直接 `cvtColor` | — | `error: (-215:Assertion failed) !_src.empty() in function 'cv::cvtColor'` |
| 6 | EOF 后 `cap.set(cv2.CAP_PROP_POS_FRAMES, 0)` | 返回 `True`，但下次 `read()` 仍 `False` | `None` |
| 7 | EOF 后 `cap.open(path)` 重新打开 | `True` | 正常帧 |
| 8 | `cap.setExceptionMode(True)` 后失败 | 抛 `cv2.error`（`cap.cpp:530`） | — |

**最容易踩的一条**：`ret=False` 时 Python 侧拿到的是 **`None`**，不是形状 `(0,0,3)` 的空数组、更不是全零图。因为 C++ 的空 `cv::Mat` 经绑定转换后变成 `None`。所以 `frame.shape`、`frame.copy()` 也都会 `AttributeError`。

### 9.5 两套可直接复制的写法

**A. 读视频文件 —— `False` 就是正常结束，退出即可**（对应 `01` 号 T1-24「无摄像头时读 mp4 保证可复现」）

```python
import cv2

cap = cv2.VideoCapture("data/raw/inspect.mp4")
if not cap.isOpened():                 # 先查设备/文件是否打开
    raise RuntimeError("打不开视频文件")

while True:
    ret, frame = cap.read()
    if not ret:
        break                          # EOF，正常收尾
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # ... 你的检测逻辑

cap.release()
```

**B. 工业相机 —— 一次 `False` 不等于断线，要容错 + 重连**（对应 `09` 号 §3 采集线程、W41–44 的 8 小时压测）

```python
MISS_LIMIT = 5                         # 连续失败多少帧才判掉线
miss = 0
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        miss += 1
        if miss < MISS_LIMIT:
            continue                   # 容忍偶发坏帧
        cap.release()
        cap = cv2.VideoCapture(0)      # 关键：重新 open
        if not cap.isOpened():         # seek(POS_FRAMES,0) 对相机无意义
            raise RuntimeError("相机断线，重连失败 → 通知上位机 / PLC 停机")
        miss = 0
        continue
    miss = 0
    # ... 处理 frame
```

> **顺带（Q07 附带发现）**：`09` 号 §3 `:293-296` 的 `AsyncCapture._loop` 里是 `ok, frame = self.cap.read(); if not ok: self.stopped = True; break` —— `ok` 就是 `ret`，但**一帧失败就永久停线程、且不重连**。产线相机瞬时掉帧会静默停采集，与 W41–44 的 8 小时压测要求不符，建议按上面的 B 改。已在 `09` §11 加交叉引用。

### 9.6 5.0 的另一种风格：用异常代替返回值

`videoio.hpp:1067` 有 `CV_WRAP void setExceptionMode(bool enable)`，本机实测 `cv2.VideoCapture.setExceptionMode` 可用：

```python
cap = cv2.VideoCapture(0)
cap.setExceptionMode(True)   # 之后失败不再返回 False，而是抛 cv2.error
ret, frame = cap.read()      # 失败时直接抛异常（报在 cap.cpp:530）
```

这更接近 Java 的 `try/catch` 习惯。**但本项目现有代码（`09` 号）统一用 `ret` 判断，不要两种风格混用**；想用就得整条采集链路一起改。

### 9.7 Java → Python 对照

| OpenCV Python | Java 里的对应物 | 差别 |
|---|---|---|
| `ret, frame = cap.read()` | `Optional<Mat> r = cap.read(); if (r.isPresent())` | Python 一次调用把「状态 + 数据」打包成元组返回 |
| `ret == False` | `BufferedReader.readLine() == null` | 都是「流结束」的信号，但 OpenCV 额外给个显式 bool |
| `ret` 作循环条件 | `Iterator.hasNext()` | `hasNext()` 先问再取；`read()` 是取完顺带告诉你成没成 |
| `frame is None` | 方法返回 `null` | Java 里 `null` 调方法报 NPE；Python 里传 `None` 给 cv2 报 `-215` 断言 |
| `setExceptionMode(True)` | 抛受检异常 + `try/catch` | 把错误从「返回值」挪到「控制流」 |

### 9.8 反常识 / 易错点清单

| # | 坑 | 正解 |
|---|---|---|
| 1 | 「`ret` 就是 `grab()` 的返回值」 | 错。是 `!image.empty()`，`retrieve()` 的返回值被丢掉了（`cap.cpp:551-561`） |
| 2 | 「`ret=False` 时 `frame` 是空数组或全黑图」 | 是 `None`。判断要用 `if not ret`，别用 `frame.size == 0` |
| 3 | 「打不开摄像头 `read()` 会报错」 | 不会，照样 `(False, None)`；循环前必须 `isOpened()` |
| 4 | 「EOF 后 `set(POS_FRAMES, 0)` 能重播」 | 实测返回 `True` 但读不回来，必须 `release()` + `open()` |
| 5 | 「`ret=True` 说明这帧画面没问题」 | 它只保证拿到非空图；过曝、模糊、运动拖影一律不管，那是检测算法的事 |
| 6 | 「视频文件和相机可以共用一套失败处理」 | 文件 EOF 该正常退出；相机才要容错重连，别把视频写成无限循环播放 |

### 9.9 自测题（S-27 增补，答案全在本节）

| 题 | 问什么 | 答案位置 |
|---|---|---|
| 1 | `ret` 是 `grab()` 的返回值吗？源码到底判的是什么？ | §9.3 |
| 2 | `ret=False` 时 `frame` 是什么？直接传给 `cvtColor` 报什么错？ | §9.4 |
| 3 | 视频 EOF 后想重播，`set(CAP_PROP_POS_FRAMES, 0)` 够不够？ | §9.4 / §9.5 |
| 4 | 相机掉线为什么不能一帧 `False` 就停机？ | §9.5 B |
| 5 | 视频文件与工业相机的失败处理为什么不能共用一套？ | §9.8 #6 |

**过关线**：按 `02` §1 的 1–5 分自评，**≥4 分**＝能不看文档讲清「ret 判的是非空图」「frame 是 None」「-215 断言」「重开而非 seek」四点。

**关联编号**：`S-27`（VideoCapture / 帧率 / 缓冲 / 抓图，`02` §6）、`T1-21` / `T1-24`（`01` §W6）、`W6` 视频与相机、`09` §3 采集并发与节拍优化；交叉引用见 `09` §11、`02` §16，台账见 `13` §4 Q07。
