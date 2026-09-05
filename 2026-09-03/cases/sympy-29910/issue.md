# integrate x**2*exp(-x**2)*ln(x)

```python
In [12]: manualintegrate(x**2*exp(-x**2)*ln(x), x)
Out[12]: 
⌠                  
⎮       2          
⎮  2  -x           
⎮ x ⋅ℯ   ⋅log(x) dx
⌡                  

In [13]: integrate(x**2*exp(-x**2)*ln(x), x)
Out[13]: 
⌠                  
⎮       2          
⎮  2  -x           
⎮ x ⋅ℯ   ⋅log(x) dx
⌡                  

In [14]: 
```

<img width="1037" height="265" alt="Image" src="https://github.com/user-attachments/assets/42cc9dc6-742f-4cb8-90bd-d30219bc25dc" />
