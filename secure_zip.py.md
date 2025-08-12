secure_zip.py
项目简介
secure_zip.py 是一个用于压缩和解压文件夹的 Python 脚本，支持 AES-256 加密和 SHA256 哈希验证。脚本提供中文交互提示，自动检测当前目录中的 ZIP 文件以选择压缩（zip）或解压（uzip）操作，适合安全地处理文件。
功能特点

自动检测：根据当前目录是否有单一 ZIP 文件，选择压缩或解压模式。
压缩（zip）：将文件夹压缩为 ZIP 文件，以 SHA256 哈希值命名，避免重复压缩。
解压（uzip）：自动验证 ZIP 文件的哈希值，支持解密和提取文件。
加密：使用 cryptography.fernet 提供 AES-256 加密，保护文件内容。
用户友好：中文提示，操作简单，支持默认当前目录。

安装要求

Python：3.6 或更高版本
依赖库：cryptographypip install cryptography



使用方法

运行脚本：
python secure_zip.py


压缩（zip）：

如果当前目录无 ZIP 文件，脚本默认执行压缩。
示例：当前目录：/home/user/docs
未检测到 ZIP 文件，将执行压缩操作
请输入文件夹或 ZIP 文件路径（按 Enter 使用当前目录/检测到的文件）：
请输入输出目录（留空则使用当前目录）：
请输入加密密码（留空则不加密）：MySecurePass123
成功：已压缩并加密到 '/home/user/docs/a1b2c3...d4e5.zip'
SHA256 哈希值：a1b2c3...d4e5




解压（uzip）：

如果当前目录有一个 ZIP 文件，脚本默认执行解压。
示例：当前目录：/home/user/docs
检测到一个 ZIP 文件：/home/user/docs/a1b2c3...d4e5.zip
将执行解压操作
哈希验证成功：a1b2c3...d4e5
请输入解密密码：MySecurePass123
请输入解压文件输出目录（留空则使用 extracted 文件夹）：
成功：已解压并解密到 '/home/user/docs/extracted'





注意事项

密码安全：建议使用强密码（12+ 字符，包含大小写、数字和特殊字符）以确保加密安全。
哈希验证：解压时会自动验证 ZIP 文件名中的 SHA256 哈希值，若文件名不匹配，可手动输入哈希值。
临时文件：压缩过程中会生成 temp.zip，异常中断可能导致残留，请手动清理。

许可证
本项目采用 MIT License，详见 LICENSE 文件。
License (English): This project is licensed under the MIT License - see the LICENSE file for details.
联系方式
如有问题或建议，请通过 GitHub Issues 反馈或联系作者 n1set
