![PyPI - Downloads](https://img.shields.io/pypi/dm/qpyr)
[![PyPI Latest Release](https://img.shields.io/pypi/v/qpyr)](https://pypi.org/project/qpyr/)
![PyPI - License](https://img.shields.io/pypi/l/qpyr)
[![codecov](https://codecov.io/gh/sabih-h/qpyr/graph/badge.svg?token=YLOSBSXWJJ)](https://codecov.io/gh/sabih-h/qpyr)


# QPYR - QR Code Generation in Python
Python package designed for creating QR codes with support for all QR code versions from 1 to 40. Designed for developers looking for a simple way to integrate QR code generation into their Python applications 🚀🚀🚀.


## Basic usage
To use the package, import and call the `main` function as follows:

```python
# Save qrcode as image
import qpyr
qpyr.main("google.com", filepath="qr1.png")
```

```python
# Show qrcode as image
import qpyr
qpyr.main("google.com", show_image=True)
```

<img src="https://raw.githubusercontent.com/sabih-h/qpyr/cbeb109d266dea0e1052ab5fa720c4a2edbf1983/docs/static/qrcode-example.png" alt="QR Code" width="200" height="200"/>


## Contributing
Contributions are warmly welcomed! Whether you're tackling a bug, adding a new feature, or improving documentation, your input is invaluable in making this library better.
