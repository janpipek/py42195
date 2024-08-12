# py42195

Tiny library in pure Python to help you keep in (running) pace.

## Installation

```bash
pip install py42195  # or `uv pip install py42195`
```

## Examples

How fast do I (well, not me) need to be to finish a marathon in 2 hours?

```python
>>> from py42195 import duration, Distance
>>> desired_pace = duration("2:00:00") / Distance.MARATHON
>>> desired_pace
pace('2:50.6')
```

What would be the speed in mph?

```python
>>> desired_speed = desired_pace.to_speed()
>>> desired_speed.mph
13.109  # + a few more digits
```

Will I be able to finish a half-marathon in 1:30 hours if I run at a pace of 4:07 min/km?

```python
>>> from py42195 import pace, Distance
>>> my_pace = pace("4:07")
>>> my_pace * Distance.HALF_MARATHON <= duration("1:30:00")
True  # 1:26:51
```

How long will it take me to run 10 miles at a pace of 5:00 min/km?

```python
>>> from py42195 import pace, distance
>>> my_pace = pace("5:00")
>>> my_distance = distance("10 mi")
>>> my_pace * my_distance
duration('1:20:28')
```

Enable the imperial units by default (note that this affect only printing):

```python
>>> from py42195 import set_unit_system, IMPERIAL, Distance
>>> with set_unit_system("imperial"):
...     print(Distance.MARATHON)
26.22 mi
```

## TODOs

- [ ] Add proper support for imperial units in printing
- [ ] Add more documentation
