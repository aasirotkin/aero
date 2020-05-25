# aero
Everything about aerodynamic

This repository contains all my aerodynamic homework.
Is is not huge enough right now, but I hope it will grow!

On present there is only one file - circulation.py

Main idea of physics that lies inside the formulas in this file was taken from Anderson.
(https://www.amazon.com/Fundamentals-Aerodynamics-John-Anderson-Jr/dp/0073398101)

Main idea of realisation was taken from awesome youtuber Josh The Engineer.
His website: http://www.joshtheengineer.com/
His explanation: https://www.youtube.com/watch?v=b8EnhiSjL3o&t=492s

My contribution is to rewrite python code in comprehensive way.
I created class Figure, which helps me to calculate circulation in more convenient way.
Also I upgrade Airfoil method, all you need is to write Airfoil name.
This name you can take from the website:
https://m-selig.ae.illinois.edu/ads/coord_database.html

There are also classes:
UIUSHelper - helps to take airfoil data (X, Y coordinates)

Airfoil(Figure) - creates airfoil shape with given name
	Input paramentrs are:
		-name - airfoil name from the given above website

Ellipse(Figure) - creates ellipse shape with given paramentrs
	Input paramentrs are:
		-a - ellipse x half-axle
		-b - ellipse y half-axle

Square(Figure) - creates square shape with given paramentrs
	Input paramentrs are:
		-a - square width
		-b - square height

Triangle(Figure) - creates triangle shape with given paramentrs
	Input paramentrs are:
		-p1(x,y), p2(x,y), p3(x,y) - coordinate points

Ogive(Figure) - creates ogive shape with given paramentrs
	Ogive is https://en.wikipedia.org/wiki/Ogive
	Input paramentrs are:
		- base_r - the radius of the base, [m]
		- nose_r - the radius of the nose, [m]
		- length - whole length from nose till base, [m]

Circulation - main class which calculates circulation and to plots result for a given Figure
