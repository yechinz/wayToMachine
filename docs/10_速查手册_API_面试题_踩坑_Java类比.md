# 10 · 速查手册：API / 面试题 / 踩坑 / Java 类比

> 用途：全程随手查、面试前突击、现场排错。来源：`../机器视觉学习路线图.md` `§4.2`（`:334-357`）、`§6`（`:636-725`）、`§7`（`:729-796`）、`§8`（`:813-838`）。
> 配套：[`00 总览`](./00_学习手册总览_路线与使用方法.md) · [`01 ToDoList`](./01_ToDoList拆解_48周动手任务清单.md) · [`02 ToStudyList`](./02_ToStudyList拆解_知识体系与自测清单.md) · 手册 `03`–`09`。

---

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
| 特征 | `ORB_create/SIFT_create/BFMatcher/findHomography` | SIFT 需 contrib；`findHomography(..., cv2.RANSAC, 3.0)` |
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
| 9 | 不学 C# | P7 必做，70% 现场软件是 C# |
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
- YOLO loss ≈ 分类损失 + 框回归（CIoU/DFL）+ 置信度；anchor-free 直接预测中心/边界偏移，省掉锚框超参。
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
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-contrib-python PySide6 pyyaml

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
| `AttributeError: module 'cv2' has no attribute 'SIFT_create'` | 装的是主包不是 contrib | 卸载主包重装 contrib；或回退 ORB（`03` §1.4） |
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
