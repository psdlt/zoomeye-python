# zoomeye-python
A simple ZoomEye API wrapper in Python.

This script provides a simple interface for fetching results `.next_page()`.
ZoomEye API has a 500 page limit for any search query. 
This script will automatically work around that by appending `+before:"..."` to the search query when it needs to go
over page 500.

# Usage

```python
from ZoomEye import ZoomEye
zm = ZoomEye("your search query here", "YOUR_ZOOMEYE_EMAIL", "YOUR_ZOOMEYE_PASSWORD", page=1, verbose=True)
zm.login()
results = zm.next_page()
```

