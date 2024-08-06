# py42195

Tiny library to help you keep in (running) pace.

## Examples

How fast do I (well, not me) need to be to finish a marathon in 2 hours?

```python
>>> from py42195 import duration, Distance
>>> desired_pace = duration("2:00:00") / Distance.MARATHON
>>> desired_pace
pace('2:50.6')
```

Will I be able to finish a half-marathon in 1:30 hours if I run at a pace of 4:07 min/km?

```python
>>> from py42195 import pace, Distance
>>> my_pace = pace("4:07")
>>> my_pace * Distance.HALF_MARATHON <= duration("1:30:00")
True  # 1:26:51
```
