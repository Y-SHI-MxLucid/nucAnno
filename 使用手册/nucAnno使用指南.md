## nucAnno使用指南

----

* [Q&A](#Q&A)
* [安装部署](#安装部署)
* [图像读入和标注](#图像读入和标注)
* [标注数据导入/导出](#标注数据导入/导出)
* [标注结果审阅](#标注结果审阅)
* [高级功能](#高级功能)
* [关于本工具](#关于本工具)

----


### 1. Q&A

* __Q1: 什么是nucAnno?__

  > nucAnno是基于Python Napari图像可视化库，为ShiLab开发的自动化fMOST胞体数据标注工具，主要是用于解决神经元轴树突追踪前的胞体定位和胞体脑区标注问题。
  >
  > 尽管目前也有种种方案来进行全自动的胞体中心检测与标注（不排除在nucAnno的后续版本中加入这些功能），但是考虑到目前fMOST图像数据不均一的质量（可能源于实验或成像过程），以及在神经元当中混杂的胶质细胞、碎屑、噪点等因素的影响，手动标注可能是最为稳妥的一种方案。因此，nucAnno通过结合Napari的点标注功能、空间自动排序算法等方式，提供了一种半自动的读图→标注→校正→结果导出的全流程方案，效率和可交互性远高于常规的ImageJ的点标注方案。
  
* __Q2: 我看到在工具目录内还有一个子目录nucRegis，这个是什么？__

  > nucRegis是与nucAnno工具相关的实验性功能，通过Python SimpleITK图像配准库和networkx连接图处理库等工具，对要标注的实验数据的降采样体块与AllenBrain标准脑区数据进行配准，从而实现近乎于全自动的脑区注释。这一功能尽管已经成功运行并取得了预期结果，但目前还缺乏充分的实验和debug，且缺乏可视化功能，因此仅限于感兴趣的使用者自行实验和发掘。
  >
  > <font color='red'>注意！</font> 安装依赖文件requirements.txt当中仅包含使用nucAnno的最低限度的依赖项。若要使用nucRegis，视你使用的版本，可能需自行安装脚本需求的依赖库，可能包括但可能不限于：
  >
  > * SimpleITK
  > * pynrrd

* __Q3: nucAnno输入何种数据、输出何种数据？__

  > nucAnno读入降采样的fMOST扫描成像数据，作为标注的原图像文件。数据的格式可以是在文件夹中以文件名正确排序的一系列tiff、png或jpg图像文件（不宜数量太多[如，>350]，否则可能导致一次无法读完），也可以是一个完整的tiff stack图像文件。
  >
  > nucAnno输出以下种类的数据：
  >
  > （1）ncas（nucAnno Session）文件。这个文件可以用于保存任何胞体标注工程。只要同时拥有标注的原图像文件，就可以随时利用ncas文件恢复之前标注的进程。
  >
  > （2）标注结果的excel文件。这一文件直观地体现被标注胞体的位置、顺序和脑区，符合shilab的标准胞体标注格式，可以直接被用于后续的流程。同时，你可以使用excel文件在nucAnno中生成"Reviewer"图层，结合标注的原图像文件，就可以对标注结果进行后期审阅和校正。
  >
  > （3）ImageJ ROISet Zip文件。这个文件是将工具的标注结果转换为ImageJ ROI Manager可以读入和显示的ROISet文件，你可以在ImageJ ROI Manager里面打开它并进行后续的审阅，但是自然地，不再支持交互式的校正和结果导出。这一功能主要是针对没有使用这一工具的用户来进行数据上的对接。
  >

* __Q4: 我能在这一工具的基础上进行进一步的开发吗？__

  > 欢迎。但是请保持这一工具的开源性，如本工具遵循的GNU GPL协议所述。如果涉及到任何学术性成果的发表，请联系并注明本工具的原作者。
  >

* __Q5: 我能将这一工具不做修改、直接打包销售或尝试其他可能的商业化手段吗？__

  > 不能。

* __Q6: 我能将这一工具发布在网上/拷贝给其他人吗？__

  > 这一工具的功能是高度特化的，拷贝给他人请联系ShiLab的相关人员确认可行性。不推荐将未进行二次开发的原工具发布在网上，如有必要理由，请联系原作者。如涉及二次开发和学术成果发表，请参照Q4。

### 安装部署

nucAnno已经部署在ShiLab的数台计算机上，如需使用，可直接联系相关人员。

如需在其他计算机上部署该工具，遵循以下步骤：

1. 系统需求：RAM ≥ 16Gb；典型的基准水平CPU如i5-1135G7或同等效能的CPU。

   <font color='Blue'>注意</font>: 工具对于显卡配置没有特殊需求。工具会应用渲染当前显示器的显卡来渲染图像，因此，假如显示器没有直接连接到高性能独显上，独显将无助于提升工具性能。参见这一讨论：

   [1]: https://forum.image.sc/t/choosing-specific-gpu-card-for-napari/68676	"Choosing specific GPU card for napari"

2. 安装包：

   nucAnno的工程发布在[Y-SHI-MxLucid/nucAnno: 神经细胞克隆自动化标注工具 (github.com)](https://github.com/Y-SHI-MxLucid/nucAnno) 。你可以在[Release Beta Release 0.0.1 · Y-SHI-MxLucid/nucAnno (github.com)](https://github.com/Y-SHI-MxLucid/nucAnno/releases/tag/v0.0.1-beta)找到文件的源代码，点击"Assets"中的任一链接均能下载源代码文件夹。建议"Source code (zip)"选项。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305211413495.png" alt="image-20240305211413495" style="zoom: 47%;" align="left"/>

3. 下载源代码安装包并解压至任意位置，这一根目录的位置接下来我们表示为<font color="Gree">/path/to/program/</font> 。目录中的内容应当大体上如图所示，可能略有出入，但一定会有nucAnno和nucRegis两个子文件夹：

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305215353642.png" alt="image-20240305215353642" style="zoom: 93.5%;" align="left"/>

4. 假如计算机没有安装Python 3.11：在子路径 <font color="Gree">/path/to/program/</font>nucAnno/install/ 中，点击安装文件并安装Python 3.11。如果你不希望新安装的Python 3.11覆盖原先环境变量中已经安装的其他版本的Python，在安装时__不要__点选 "Add python.exe to PATH"选项。请完全按照默认选项进行安装。安装后，找到程序的安装路径，这一路径接下来我们表示为：<font color="Orange">/path/to/interpreter/</font> 。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305212219284.png" alt="image-20240305212219284" style="zoom: 67%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305212804619.png" alt="image-20240305212804619" style="zoom: 59.7%;" align="left"/>

5. 在任意位置创建一个空文件夹，这一空文件夹的路径接下来表示为<font color="Pink">/prefix/to/environment/</font> 。

6. 注意到nucAnno/install/ 中有一个文件virtualenv.pyz。接下来，打开Windows Powershell，输入以下命令：

   ```powershell
   cd /prefix/to/environment/
   /path/to/interpreter/python.exe virtualenv.pyz nucAnno
   # 此处等待片刻，虚拟环境即创建完成，关闭WIndows Powershell
   ```

   我们将<font color="Pink">/prefix/to/environment/</font>nucAnno/ 这一目录接下来表示为<font color="Cyan">/path/to/environment/</font> 。

7. 接下来，我们需要在Windows Powershell程序上右键"以管理员身份运行"。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305214639040.png" alt="image-20240305214639040" style="zoom:77.8%;" align="left"/>

   在打开的命令行窗口中输入：

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass
   # 执行策略更改
   # 执行策略可帮助你防止执行不信任的脚本。更改执行策略可能会产生安全风险，如 https:/go.microsoft.com/fwlink/?LinkID=135170中的 about_Execution_Policies 帮助主题所述。是否要更改执行策略?
   # [Y] 是(Y)  [A] 全是(A)  [N] 否(N)  [L] 全否(L)  [S] 暂停(S)  [?] 帮助 (默认值为"N"):
   # 输入Y或者A，然后回车，随后即可关闭WIndows Powershell
   ```

8. 接下来，重新以常规权限打开Windows Powershell。输入以下命令：

   ```powershell
   /path/to/environment/Scripts/Activate.ps1
   python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
   python -m pip install --ignore-installed -r /path/to/program/nucAnno/install/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   # 此步骤需要保持计算机联网。可能需要消耗几分钟到十几分钟的时间，请耐心等待直到运行结束。这一步将程序运行所需的依赖项安装至虚拟环境中。
   ```

9. 最后，将<font color="Gree">/path/to/program/</font>nucAnno/install/run_nucAnno.ps1这一文件拷贝至程序根目录<font color="Gree">/path/to/program/</font> 。 

   ```powershell
   /path/to/environment/Scripts/Activate.ps1
   #虚拟环境激活文件的路径，将文件中这一句改为和实际的虚拟环境路径对应
   python ./nucAnno/main.py
   #启动程序
   ```

10. 至此部署完成。使用时只需在根目录的run_nucAnno.ps1文件上右键，选择"使用Powershell运行"即可。

    <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240305230419083.png" alt="image-20240305230419083" style="zoom:67%;" align="left"/>

### 图像读入和标注

1. 程序启动后的界面如图所示。视显示器的分辨率等因素，各组件一开始可能没有处在合适的大小，请自行拖动其边缘进行调整。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306153528318.png" alt="image-20240306153528318" style="zoom: 33%;" align="left"/>

2. 读入欲标注的原图像文件时，点击界面右上角target栏目的"Select Files"，打开文件选择窗口。这里，你可以选择单个的Tiff Stack文件，也可以在图像文件夹中Ctrl+A选取一系列图片同时读入。在文件选择窗口点击打开后，还需要在target栏目下方点击"Read Image"来开始读入图片。

   <font color='red'>注意！</font> 读入一系列图片时，请确保这些图片在文件夹中是__正确排序__的。

   <font color='red'>注意！</font> 当你选择一系列图片时，请确保图片的数量__不会太多__（例如，不超过350张）。否则将会导致文件名称超出长度的最大限制，从而使得读入出错。

   <font color='red'>注意！</font> __请勿尝试__在左上角"File"菜单、或直接将文件拖入界面窗口来打开图像文件。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306152439045.png" alt="image-20240306152439045"  align="left"/>

3. 在经过大约数秒钟到十几秒钟等待后，界面的左下角图层栏目将新增Reviewer、Image Stack和Clone Marker三个图层。此时意味着图片读入完毕。点击Image Stack图层，调节左上角contrast limits的上界至极低，然后向后滚动鼠标滚轮（缩小图片），直至图像出现在视野中。将图像拖动到视野正中并重新放大，重新调节contrast limits的上界，直至图像对比度能够清晰地区分出神经元胞体、又不至于忽略掉比较暗的细胞。至此，图片的读入和调整完成。

   > 可选的操作：你可以将Image Stack层的opacity调节至0.85左右，这样就可以在后续标注时看到以圆形标出的标记胞体的位置范围。但是这一功能在实际操作中作用往往并不明显。

   <font color='Blue'>注意</font> 由于某些未知的原因，读入的fMOST图片会显示在初始视野的右下方（这一点是fMOST图像独有的），因此一开始视野中没有任何图片是正常的。你需要做的就是拉远视角直到找出图像在哪里。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306161009552.png" alt="image-20240306161009552" style="zoom: 38.4%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306161226205.png" alt="image-20240306161226205" style="zoom:38.4%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306162321063.png" alt="image-20240306162321063" style="zoom:27.8%;" align="left"/>

4. 在说明标注流程之前，首先在此说明Napari平台所支持的几种图层类型，包括：

   * Points

   * Shapes

   * Labels

   * Image

   以及没有显式体现在软件界面的

   * Tracks

   * Surface

   * Vectors

   * Graphs （尚未发布的实验性功能）

   关于这些图层的详细描述和使用教程，请参见：

   * [Layers at a glance — napari](https://napari.org/stable/guides/layers.html)
   * [Using layers — napari](https://napari.org/stable/howtos/layers/index.html)
   * [napari.layers — napari](https://napari.org/stable/api/napari.layers.html)

   我们在nucAnno中使用Points图层来标记胞体位置，并使用Shapes图层来自动显示被标记胞体的区域。

5. 我们每标记一个稀疏标记的神经元的克隆，即需要添加一个胞体标注图层。例如图中我们想要标记这个RSP脑区的克隆。这个克隆在邻接的两个Z位置上有细胞分布。我们首先需要在左下角图层栏目中，点击"New points layer"按钮，新建一个Points图层。创建完毕后选中新图层，点击左上方工具栏的"Add points"按钮，进入添加胞体标记的工作。

   <font color='Blue'>注意</font> Points图层的工具栏里面，最上方四个按钮分别为删除标点、增加标点、选中标点、移动图像。具体的用法请参照4当中的Napari平台相关教程。值得一提的是，在"增加标点"模式下，依然具有拖拽图像、滚轮放大缩小图像的功能。但是，在选择"增加标点"模式后，必须用鼠标拖拽一次图像，才能够正常地使用键盘←→方向键来在stack中切换不同帧/层的图像。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306165942339.png" alt="image-20240306165942339" style="zoom:38.5%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306170248987.png" alt="image-20240306170248987" style="zoom: 80%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306170637167.png" alt="image-20240306170637167" style="zoom:79%;" align="left"/>

6. 依次用增加标点工具标注在该克隆分布在各层的神经元胞体。这个标注过程不需要按照任何顺序，只要保证克隆中分布在各层的所有神经元胞体都被标注即可。你可以随时点选左上工具栏中"out of slice"选项，将各层的标注点投射到当前层来查看它们的分布，如下图所示。其中被红色三角标记的标注点是被标注在临近层上的，实际位置不在该层。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306172415452.png" alt="image-20240306172415452" style="zoom:45%;" align="left"/>

7. 标注完成后，你需要额外增加一个"参照点"。这个参照点标定了当前克隆所在脑区的皮层最内侧的方向。示例和原理如下图所示。工具会根据各个标注的胞体到"参照点"的距离进行排序，来确定各个胞体的内外顺序，并将之体现在序号中。

   > 这当然不是最准确的方法。确定神经胞体皮层内外顺序的金标准当然是计算空间中各个标点到脑区分层边界这一3维曲面的法向距离，而且还要考虑内外所有的分层。很显然，这已经超出了工具作者孱弱的数学能力。欢迎各位提出计算方法上的改进建议。

   <font color='red'>注意！</font> 请确保参照点是最后一个添加的。算法上，最后一个添加的点会被视作参照点。

   <font color='Blue'>注意</font> 有时由于脑区的分层具有奇怪的形状，无论参照点处在何种位置，都不能形成完全正确的胞体内外排序。此时你可以取一个"尽可能正确"的位置，后续在交互式表格中修改胞体的次序信息。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306174134257.png" alt="image-20240306174134257" style="zoom:62%;" align="left"/>

8. 在标注完"参照点"后，你需要在右侧功能区Assign Points模块定义标注克隆的脑区名称。例如在此处，我们标记的克隆处于RSP脑区，则我们需要在group name栏目输入"RSP"，然后点击下方的按钮"Assign Points"。点击之后，你将会看到如下图显示的几个变化：

   * 标记的神经元胞体，标点变成随机颜色的"+"形，并按照其内外层顺序被命名，胞体编号以标签的形式标注在胞体上；
   * 右边的交互式表格中出现了该层的胞体标注信息；
   * 左边的图层栏目中，新标记的图层将会按照脑区名称被重命名，可见性改变为不可见，位置移动至Image Stack下方。

   > 实际上，你看到的标点和文字标签并不是来源于新标注图层（已经被设置为不可见）上的显示。各个克隆标注图层的标点位置和胞体编号的信息会被合并、并统一在Reviewer层进行显示。这一操作是为了使得同一时间在界面显示（即设置为可见）的图层数量不会随着标注克隆数量的增加而增加，从而有效地改善在低配置计算机上的运行流畅度。

   <font color='Blue'>注意</font> 对于基础的标注功能而言，Assign Points模块其他部分的设置不需要做任何有别于默认设置的改变。值得一提的是"random color"选项：这一选项默认选中，使得每一次完成整个克隆标记后，克隆的标点和文字标签会以随机颜色（相应的随机生成函数经过HSV表示处理，确保不会产生低饱和度/低亮度的颜色）显示。倘若取消选中，克隆的标点和文字标签会统一显示为红色。

   至此，单个神经元克隆的胞体标注就已经完成。若要标注复数个克隆，重复步骤5~8的操作。后续的克隆标注图层将会逐层追加在图层栏目中（并始终处于Image Stack和Reviewer图层下方）；这些标注图层的胞体位置信息和胞体编号将会被追加至右侧的可交互式表格中。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306193223908.png" alt="image-20240306193223908" style="zoom:75%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306194033622.png" alt="image-20240306194033622" style="zoom: 40%;" align="left"/>

9. 在解释如何对标注结果进行修改之前，我们首先检视右侧可交互式表格的各列内容。对于各列内容的解释如下图：

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240306201225413.png" alt="image-20240306201225413" style="zoom:67.8%;" align="left"/>

   表格的各项内容是可修改的。但是非常不建议直接修改总表的内容，除非在Reviewer模式下（参见本指南的第5章：nucAnno的标注结果审阅）。

   修改特定的标注图层有两种方法：

   * 在表格中修改。这种方法适用于先前标注结果有个别点顺序有误需要进行交换的情况；
   * 对图层进行重新标注。这种方法适用于先前标注结果存在多标、少标、参照点选择需要进行调整、脑区名称需要改变等情况。

   __<font color="Purple">在表格中修改</font>__

   1. 点选需要修改的克隆标注图层，然后点击右侧功能栏目中的"Get Feature"，交互式表格中将仅显示该层的数据。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307133551260.png" alt="image-20240307133551260" style="zoom: 38.3%;" align="left"/>

   2. 在表格中，修改"胞体编号"和"Order"两栏的内容，以交换两个胞体的编号顺序。修改后点击右侧功能栏目中的"Update Feature"。

      <font color='red'>注意！</font> 如果不是在Reviewer模式下，请勿选中"proof read"选项。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307135659561.png" alt="image-20240307135659561" style="zoom: 87.3%;" align="left"/>

   3. 之后，图像中的标记以及总表中的数据都会被更新至正确的次序。

      <font color='Blue'>注意</font> 在旧版本中（如安装在ShiLab某些计算机上的版本），存在如下Bug：当总表数据被更新后，被更改的克隆标注层的可见性将变为"可见"（如下图中左下红色方框所示）。这并不影响软件的正确运行，但这样可见的图层积累过多将可能导致软件流畅度降低。需要手动将可见性改为"不可见"。这一Bug已经在GitHub的最新版本中被修复。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307140418076.png" alt="image-20240307140418076" style="zoom:38.4%;" align="left"/>

   __<font color="Purple">对图层进行重新标注</font>__

   1. 将需要修改的图层拖拽至图层栏的最上层，可见性更改为"可见"。同时将Reviewer层的可见性修改为"不可见"。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307144950806.png" alt="image-20240307144950806" style="zoom:100%;" align="left"/>

   2. 选中需要修改的点，点击删除按钮将点删除。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307144520821.png" alt="image-20240307144520821" style="zoom:49.4%;" align="left"/>

   3. 删除后，添加新的正确标点。新添加的点会具有"+"形格式并带有无意义的文字标签，请无视这些标签。添加后不要忘记添加参照点，并点击右上"Assign Points"按钮。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307145347309.png" alt="image-20240307145347309" style="zoom:38.45%;" align="left"/>

   4. 之后，图像上的标记、总表中的数据都会被更新。克隆标记图层的位置、可见性、Reviewer图层的可见性等设置都会恢复至之前的状态。你可以直接继续其他克隆的标注。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307145707584.png" alt="image-20240307145707584" style="zoom:38.3%;" align="left"/>

10. 在一些情况下，我们删除了一些之前标注的图层。例如在下图中，我们标记了SSp-1、SSp-2和SSp-3三个处于SSp区的克隆（请忽略图中SSp-3标点稀奇古怪的位置，这是随机标上去用于测试功能的）。现在我们认为SSp-2的克隆标记不妥，因此将其删除。现在我们希望将这一删除的结果体现出来，即：

   * 将现在的SSp-3克隆重新命名为SSp-2，因为它之前的SSp-2已经被删除了；
   * 将改变体现至数据总表。

   此处我们只需要点击右侧功能区的"Rearrange Group Idx"即可。点击后，工具将会自动计算目前存在的图层，来决定其编号，并将结果反映到胞体编号标签以及数据总表中。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307150854324.png" alt="image-20240307150854324" style="zoom:39.8%;" align="left"/>

  



















 重排后的效果如图：

<img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307192804962.png" alt="image-20240307192804962" style="zoom:39.8%;" align="left" />

<font color='Blue'>注意</font> 有时我们将之前标注的某个克隆标注图层的脑区重命名至其他脑区后，也会产生相似的问题，需要通过重排来解决。



### 标注数据导入/导出

正如Q&A部分所叙述的那样，nucAnno可以导出如下三种文件：

* 标注进程文件 .ncas
* 标注结果文件 .xlsx
* ImageJ ROISet文件 .zip

1. __标注进程文件的导出和导入__

   <font color="Purple">__导出 .ncas文件__</font>

   在完成标注、或者标注到中途由于某种原因必须停止标注的情况下，可以将标注进程保存到.ncas文件中。你需要在右侧功能栏目的"Save Annotation Session"部分，设定save prefix栏目的保存路径。注意这一路径既可以是新文件命名，也可以是已经存在的文件（将会覆盖已存在的文件）。设定保存文件名时，不必特地加上.ncas后缀。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307195429473.png" alt="image-20240307195429473" style="zoom:123%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307195614693.png" alt="image-20240307195614693" style="zoom: 50%;" align="left"/>

   设定保存路径后，点击"Save Session"，进程文件即保存至相应路径。

   <font color="Purple">__导入 .ncas文件__</font>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307202843769.png" alt="image-20240307202843769" style="zoom:113%;" align="left"/>

   在右侧功能栏目的"Load Annotation Session"部分，选择需要导入的进程文件。然后点击下方"Load Session"。进程文件虽然不会保存注释的整个原图像文件（可能高达数个Gb大小），但会记录这个原图像文件的路径。假如你确定进程文件所标注的图像文件目前就在之前所记录的路径，那么可以选中"load path"栏目下方的"auto image load"选项。如果文件路径已经改变，就不要点选这个选项，而是在导入Session之后重新通过"Read Image"功能读入图像。之后，即可以从上次的进度开始、继续对图像进行标注。

   <font color='red'>注意！</font> 在一些旧版本中，存在（1）不点选"auto image load"选项、导入进程文件发生报错，以及（2）在导入进程之后单独读入图像，产生冗余的Clone Marker及Reviewer图层，且Image Stack图层不在正确次序的bug。在GitHub发布的最新版本中，这一bug已被修复。在出现bug（1）时，可以忽略报错信息，这不会产生任何影响；出现bug（2）时，可以手动删除冗余的图层，并将Image Stack图层拖拽至正确的位置（Reviewer图层下、Clone Marker和其他克隆标注图层上）。

2. __标注结果文件的导出和导入__

   <font color="Purple">__导出 .xlsx文件__</font>

   与导出.ncas文件的方法类似，你需要在右侧功能栏目的"Save Result to Excel"部分，设定save prefix栏目的保存路径。注意这一路径既可以是新文件命名，也可以是已经存在的文件（将会覆盖已存在的文件）。设定保存文件名时，不必特地加上.xlsx后缀。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307210128970.png" alt="image-20240307210128970" style="zoom:113%;" align="left"/>

   导出的文件将具有颜色格式，使得不同的克隆组被颜色区分，如下图所示。目前还无法仅改变具有内容的特定列的颜色。如果你认为这样的着色方案很丑，可以在Excel文件中自行调整。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307210723245.png" alt="image-20240307210723245" style="zoom:45.5%;" align="left"/>

   <font color="Purple">__导入 .xlsx文件__</font>

   与导入.ncas文件不同，导入标注结果的.xlsx文件不会产生新的标注进程，文件本身也不包含标注的原始图像的路径信息。因此，你必须首先按照本指南第三部分"nucAnno的图像读入和标注"的内容，首先读入原始图像、生成一个空的标注进程，然后在右侧功能栏目的"Load Reviewer Layer"部分，选择需要导入的进程文件，之后点击"Load Reviewer Layer"按钮，将之前导出的标注结果表格导入为一个可视化的Reviewer图层（会覆盖原有Reviewer图层的内容）。导入的标注结果同时也将体现在可交互式表格中，便于审阅人员对nucAnno的标注结果进行审阅。

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307211546002.png" alt="image-20240307211546002" style="zoom:113%;" align="left"/>

   <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307211745152.png" alt="image-20240307211745152" style="zoom:35%;" align="left"/>

   [导入后的结果。图上的点系用于测试，并非显示错误。]

3. __ImageJ ROISet文件的导出__

   目前工具支持将结果导出为ImageJ ROISet文件，以便利那些宁可使用ImageJ来浏览本工具标注结果的~~保守主义者~~用户；但并不能导入和显示ROISet文件。

   1. 在右侧功能栏目的"Save Result to Image ROI"区域，首先选择上方的文件保存位置。同样的，不需要在文件名后面加上"zip"后缀。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307212616404.png" alt="image-20240307212616404" style="zoom:100%;" align="left"/>

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307212723391.png" alt="image-20240307212723391" style="zoom:46%;" align="left"/>

      然后选择下方的roi sample文件路径。在<font color="Gree">/path/to/program/</font>nucAnno/sample_data/ 这一路径下，有一个文件"testROISet.zip"，在打开的窗口中选择这一文件。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307213122808.png" alt="image-20240307213122808" style="zoom:46%;" align="left"/>

      

   2. 在两个路径都选择后，点击"Save ROIZip"按钮。一个ImageJ ROI Zip文件即保存至相应路径。你可以在ImageJ的ROI Manager功能中打开它。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307214536487.png" alt="image-20240307214536487" style="zoom:54%;" align="left"/>

      <font color='Blue'>注意</font> 关于ImageJ ROI Manager的使用方法，请自行参考相关的网上教程。这里仅作一点提醒：为了能在图像上正确显示标点的胞体编号标签，你需要在ROI Manger的 More >> → Options... 窗口中点选 "Use ROI names as labels"选项。

      <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307214919711.png" alt="image-20240307214919711" style="zoom:109%;" align="left"/>
   
   <font color='red'>注意！</font> 在一些旧版本中，存在"加载进度文件/结果文件后直接将结果导出为ROISet文件将会报错"的bug。如果你在当前进度下存在已经标注好的多个克隆标记图层，则可以通过先点击右侧功能栏目中"Generate Result"按钮，然后再导出ROISet文件来解决。这一bug在GitHub发布的最新版本中已被修复。

----

> ᕕ( ᐛ )ᕗ ᕕ( ᐛ )ᕗ__至此，你已掌握了对全脑扫描成像图像的神经元克隆胞体标注方法。__ᕕ( ᐛ )ᕗ ᕕ( ᐛ )ᕗ ᕕ(;´ヮ`)ᕗ

----

### 标注结果审阅

在通过本指南第4部分"标注数据导入/导出"指引下，当你导入了已经标记好的结果xlsx文件到Reviewer图层，即可以开始标注结果审阅。审阅过程中不能对各个克隆的标点进行重新标注，仅能通过修改可交互式表格中的内容——正如"图像读入和标注"部分说明的那样，对各个克隆的胞体编号和次序进行调整。在对总表进行调整后，需要点选右侧功能栏目中"Update Feature"按钮，对Reviewer图层的标注结果进行更新。__<font color="Orange">但与之前介绍的、针对各个单独的克隆标注图层的表格进行修改的方法不同的是：（1）你不需要预先点击"Get Feature"按钮；（2）在点击"Update Feature"按钮时，需要确保"proof read"选项被选中</font>__。

<img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307221151237.png" alt="image-20240307221151237" style="zoom:117%;" align="left"/>

### 高级功能

* __对于软件默认显示选项的调整：__

  在<font color="Gree">/path/to/program/</font>nucAnno/configurations.py 文件中，你可以调整软件的一些默认显示选项。这些选项的意义在文件的注释文本中已经有充分的说明，在这里就不再赘述。

  <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307221849263.png" alt="image-20240307221849263" style="zoom:80%;" align="left"/>

* __nucAnno自动配准功能的使用：__

  nucRegis利用SimpleITK配准库和networkx图处理库，对实验数据降采样得到的脑图像、AllenBrain标准脑图像以及脑区注释数据进行空间上的仿射变换配准，最终得到脑区注释信息在实验得到的图像数据上的空间分布。在标注时，工具会根据克隆标注图层各个点的位置，进行kNN最近邻搜索来决定各个标点的所属脑区，并根据拥有最多标点的脑区来自动命名当前的克隆标注图层，从而省去了人为提供当前克隆标注的脑区位置信息这一过程。

  <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307223537334.png" alt="image-20240307223537334" style="zoom:71%;" align="left"/>

  在使用nucAnno自动配准功能时，首先需要导入nucRegis所生成的（1）配准完成的脑区注释文件；（2）脑区分结点映射至主节点的映射文件，来生成一个脑区自动分配的kNN模型。接着，在Assign Points模块，需要点选"auto assign"选项，来开启自动配准功能。

  <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307223853304.png" alt="image-20240307223853304" style="zoom:50%;" align="left"/>

  <img src="C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20240307223919488.png" alt="image-20240307223919488" style="zoom:50.3%;" align="left"/>

  如果你对于这部分功能、以及这部分功能的继续开发感兴趣，可以联系作者。


### 关于本工具

----

关于本工具的合适使用场景的解释权归ShiLab相关负责人员所有。

联系作者：yul_shi@outlook.com