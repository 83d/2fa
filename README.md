# 2FA / TOTP 工具包

本仓库提供简单的 [RFC 6238 TOTP](https://www.rfc-editor.org/rfc/rfc6238) 示例，包含 Python 命令行版本和浏览器 JavaScript 版本。

Python 脚本使用开源库 [PyOTP](https://github.com/pyauth/pyotp)。JavaScript 网页使用本地保存的开源库 [OTPAuth](https://github.com/hectorm/otpauth)，验证码直接在浏览器中计算。两个版本生成验证码时都不需要后端服务。

## 仓库结构

```text
2fa/
├── python/
│   └── totp.py              # 基于 PyOTP 的命令行生成器
├── requirements.txt         # Python 依赖及固定版本
└── javascript/
    ├── index.html           # 可离线使用的浏览器界面
    ├── test.js              # RFC 6238 JavaScript 冒烟测试
    └── vendor/
        ├── otpauth.umd.min.js
        └── LICENSE-*        # 第三方软件许可证
```

## Python 版本

安装 PyOTP 并运行脚本：

```console
python -m pip install -r requirements.txt
python python/totp.py
```

密钥通过隐藏输入框读取，不会直接显示在终端，也不会进入命令历史记录。核心用法如下：

```python
import pyotp

print(pyotp.TOTP("JBSWY3DPEHPK3PXP").now())
```

## JavaScript 版本

直接使用浏览器打开 `javascript/index.html` 即可。网页从本地 `javascript/vendor` 目录加载 OTPAuth，所有计算均在浏览器中完成，不会发送外部网络请求，也不会把密钥保存到 `localStorage` 或 Cookie。

网页功能包括：

- 验证 Base32 密钥格式
- 每 30 秒自动刷新并显示倒计时
- 一键复制验证码
- 提供公开的演示密钥
- 使用内容安全策略阻止网络连接

也可以使用 Node.js 运行 RFC 6238 冒烟测试：

```console
node javascript/test.js
```

用于正式环境时，建议继续将第三方脚本保存在本地，并在升级依赖前检查更新内容。

## 安全说明

TOTP 密钥相当于验证器应用中保存的种子。任何获得该密钥的人都可以生成相同的验证码。

- 不要把真实密钥放入网址、Git 仓库、日志、截图或命令历史记录。
- 保持设备系统时间准确。
- 不要在网页中加入统计、广告或其他远程脚本。
- 服务端应用必须妥善加密和保护密钥、使用 TLS、限制验证频率，并在验证码成功使用后拒绝重复提交。
- 对于重要账户，优先使用经过充分审查的验证器应用，或采用可抵抗钓鱼攻击的 FIDO2/WebAuthn 安全密钥。

## 第三方软件

JavaScript 页面包含 OTPAuth 9.4.0 及其打包依赖 noble-hashes 1.7.1。详细信息请参阅 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 `javascript/vendor` 目录中的许可证文件。

## 许可证

本项目自行编写的代码采用 [MIT 许可证](LICENSE)。仓库内附带的第三方依赖继续遵循其各自的许可证。
