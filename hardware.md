```
Olimex ICE40 EVB 34 Pin Pinout

 +---------------------------  -------------------------------+
 |P33 P31 P29 P27 P25 P23 P21 P19 P17 P15 P13 P11 P9   P7  P5 |
 | p4  p3  p2  p1  e1  e2  e3  e4  e5  e6  e7  e8  e9  e10    |
 |                                                            |
 |P34 P32 P30 P28 P26 P24 P22 P20 P18 P16 P14 P12 P10         |
 | p5  p6  p7  p8  p9 p10 p11 p12 p13 p14 p15 p16 p17         |
 +------------------------------------------------------------+
```
cnc:
XStep p2  P29
XDir  p3  P31
XEn   p4  P33
YStep p5  P34
YDir  p6  P32
YEn   p7  P30
ZStep p8  P28
ZDirc p9  P26
ZEn   p14 P16
plotter:
XDir  p2  P29    X0  e1  P25
XStep p3  P31   
XEn   p4  P33
YDir  p5  P34    Y0  e2  P23
YStep p6  P32
YEn   p7  P30
ZDir  p8  P28    Z0  e3  P21
ZStep p16 P12
ZEn   p14 P16
                 Stop e4  P19

p9 (P26) is defect on CNC breakout board!
