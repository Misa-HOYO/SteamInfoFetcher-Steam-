# Steam 游戏信息抓取工具

一个 Python 脚本，通过输入 Steam 商店链接或游戏名称，自动搜索并获取游戏详细信息，下载截图和封面图，并生成 HTML 信息文件。适合需要批量整理 Steam 游戏资料的用户。

## 功能特性

- **两种输入方式**  
  支持 Steam 商店链接（自动提取 appid）或游戏名称（使用 Steam 商店搜索，支持中文）。
- **获取详细信息**  
  通过 Steam 官方 API 获取游戏的中文名称、简短简介、详细描述（HTML 格式）以及所有截图和封面图链接。
- **多线程下载图片**  
  使用 `ThreadPoolExecutor` 并行下载截图和封面图，大幅提升速度。
- **独立文件夹保存**  
  每个游戏以 `appid_游戏名` 命名文件夹，图片和 HTML 文件互不干扰。
- **自动打开结果文件夹**  
  下载完成后自动打开该游戏的文件夹（仅 Windows）。

## 环境要求

- Python 3.6+
- 依赖库：`requests`, `beautifulsoup4`

## 安装依赖

```bash
pip install requests beautifulsoup4
使用方法
修改保存路径（可选）
脚本默认将文件保存到运行目录下的 Save 文件夹中。
如需更改，请编辑脚本中的：

python
import os
save_folder = os.path.join(os.path.dirname(__file__), "Save")
运行脚本

bash
python steam_fetch.py
根据提示输入

输入 Steam 商店链接，例如：https://store.steampowered.com/app/1091500/

或输入游戏名称，例如：赛博朋克2077、Cyberpunk 2077

若输入名称，脚本会显示搜索结果列表（最多10条），输入序号选择游戏。

脚本自动获取信息、下载图片、生成 HTML 文件并打开文件夹。


处理完成后会继续提示输入下一个游戏，可连续处理多个游戏。
注意：当前版本没有退出条件，需按 Ctrl+C 中断程序。

输出文件结构
每个游戏保存在 Save\<appid>_<游戏名称>\ 文件夹中：

text
Save/
└── 1091500_赛博朋克2077/
    ├── screenshot_000.jpg
    ├── screenshot_001.jpg
    ├── ...
    ├── header.jpg              # 封面图
    └── game_info.html          # 游戏信息页面
game_info.html 内容包含游戏原名、简介和详细描述，可直接用浏览器打开查看。其简洁格式类似：

text
游戏原名: <名称>

游戏简介: <简介>

<详细描述 HTML>
配置说明
并发线程数：脚本中 max_workers = 10，可根据网络状况调整。建议设为 3~5 以避免触发 Steam 限流。

语言设置：API 请求已带 l=schinese&cc=cn，确保返回中文信息。商店搜索同样设置为中文。

SSL 证书验证：请求中使用了 verify=False，忽略 SSL 证书验证。如有安全顾虑可删除该参数（但可能因为证书问题导致请求失败）。

注意事项
Steam 商店搜索对中文支持有限，部分游戏中文名可能搜不到。若搜索无结果，请尝试输入英文名或直接使用商店链接。

图片下载为 IO 密集型操作，多线程能显著提速，但并发过高可能被 Steam 限制，请酌情调整。

自动打开文件夹使用了 os.startfile，仅适用于 Windows。其他系统请自行替换为相应命令（如 macOS 的 open，Linux 的 xdg-open）。

生成的 HTML 保留了详细描述中的原始 HTML 样式（包括外部图片），打开时需要网络加载图片。

本工具仅供个人学习使用，请勿批量抓取或违反 Steam 服务条款。

常见问题
Q: 中文名搜索不到游戏？
A: 尝试输入游戏的英文名，或直接在 Steam 商店页面复制链接粘贴到脚本中。

Q: 下载速度慢或失败？
A: 检查网络是否正常；可尝试降低 max_workers；如果部分图片下载失败，可能是链接失效或被限流，稍后重试。

Q: 程序无法自动打开文件夹？
A: 确保运行环境为 Windows；若为其他系统，请修改 os.startfile 部分。

Q: 脚本报错 FileNotFoundError？
A: 请检查 save_folder 路径是否有写入权限，或修改为已存在的绝对路径。

Q: 如何退出程序？
A: 当前版本无内置退出命令，按 Ctrl+C 即可中断。
