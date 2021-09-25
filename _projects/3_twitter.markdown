---
layout: page
title: twitter bots
img: /assets/img/nathan-dumlao-4FHF4kCnj8A-unsplash.jpg
importance: 1
category: fun
---

### [Robot GALAH](https://twitter.com/RobotGALAH)

Robot GALAH tweets once per hour, giving the details of a random star from the Third Data Release of the GALAH Survey.

{% twitter https://twitter.com/RobotGALAH/status/1414383914769022980 %}


#### Technical details
The bot is run from a Raspberry Pi 2 Model B. It is written in Python, because that is my language of choice. [The code for the bot is found on GitHub](https://github.com/jeffreysimpson/robot_galah).

Each hour, a random star is selected from the [GALAH DR3 catalogues](https://www.galah-survey.org/dr3/the_catalogues/). There is then a check of [SIMBAD astronomical database](http://simbad.u-strasbg.fr/simbad/) at the Centre de Données astronomiques de Strasbourg (CDS) to find if there an entry for the star and a ''nice'' name for the star. The tweet text is composed that includes when we observed the star, which constellation it is found in, its distance, age, and mass, and a link the [CDS Portal](http://cdsportal.u-strasbg.fr). 

For the plots of the stellar paramaters and orbital properties, it is basically just a bunch of bespoke ``matplotlib`` convenience functions that I wrote for plotting GALAH data. I use [``mpl-scatter-density``](https://github.com/astrofrog/mpl-scatter-density) to make the background distributions.

To retrieve a colour JPEG for the 15 arcmins around the star, I use a combination of tools provided by CDS: [MOC Server tool](http://alasky.u-strasbg.fr/MocServer/query) and [``hips2fits``](http://alasky.u-strasbg.fr/hips-image-services/hips2fits). The MOC Server identifies the list of sky surveys that the star is found in, and then ``hips2fits`` is used to download the image from the ''best'' survey.

The reduced, normalized spectrum of the star are retrieved using the [Simple Spectral Access](https://www.ivoa.net/documents/cover/SSA-20071220.html) protocol from [Data Central](https://datacentral.org.au/), and then plotted with ``matplotlib``.
