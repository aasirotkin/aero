# aero
Everything about aerodynamics

This repository contains all my aerodynamics homework.
It is not huge enough right now, but I hope it will grow!

At present there is only one file - circulation.py

Main idea of physics that lies inside the formulas in this file was taken from Anderson.
(https://www.amazon.com/Fundamentals-Aerodynamics-John-Anderson-Jr/dp/0073398101)

Main idea of realisation was taken from awesome youtuber Josh The Engineer.
His website: http://www.joshtheengineer.com/
His explanation: https://www.youtube.com/watch?v=b8EnhiSjL3o&t=492s

My contribution is to rewrite python code in a comprehensive way.
I created a class Figure, which helps me calculate circulation in a more convenient way.
Also I have upgraded Airfoil method, all you need is to write Airfoil name.
This name you can take from the website:
https://m-selig.ae.illinois.edu/ads/coord_database.html

Also there are classes:
UIUSHelper - helps to take airfoil data (X, Y coordinates)

Airfoil(Figure) - creates airfoil shape with given name
	Input parameters are:
		-name - airfoil name from the website given above

Ellipse(Figure) - creates ellipse shape with given parameters
	Input parameters are:
		-a - ellipse x half-axle
		-b - ellipse y half-axle

Square(Figure) - creates square shape with given parameters
	Input parameters are:
		-a - square width
		-b - square height

Triangle(Figure) - creates triangle shape with given parameters
	Input parameters are:
		-p1(x,y), p2(x,y), p3(x,y) - point data

Ogive(Figure) - creates ogive shape with given parameters
	Ogive is https://en.wikipedia.org/wiki/Ogive
	Input parameters are:
		- base_r - the radius of the base, [m]
		- nose_r - the radius of the nose, [m]
		- length - whole length from nose till base, [m]

Circulation - main class which calculates circulation and plots result for a given Figure
