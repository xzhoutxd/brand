#!/bin/sh
DIR=`pwd`
cd $DIR
/usr/local/bin/python $DIR/chanelBage.py > $DIR/log/chanel_bage.log

/usr/local/bin/python $DIR/diorBag.py > $DIR/log/dior_bag.log

/usr/local/bin/python $DIR/givenchyBage.py > $DIR/log/givenchy_bag.log

/usr/local/bin/python $DIR/armaniBag.py > $DIR/log/armani_bag.log

/usr/local/bin/python $DIR/bottegavenetaBage.py > $DIR/log/bottegaveneta_bag.log

/usr/local/bin/python $DIR/louisvuittonBage.py > $DIR/log/louisvuitton_bag.log

/usr/local/bin/python $DIR/dolcegabbanaBag.py > $DIR/log/dolcegabbana_bag.log

/usr/local/bin/python $DIR/yslBage.py > $DIR/log/ysl_bag.log

/usr/local/bin/python $DIR/bossBage.py > $DIR/log/boss_bag.log

/usr/local/bin/python $DIR/ferragamoBage.py > $DIR/log/ferragamo_bag.log

