variant_true_rng = true;

%%%%%%%%%%

BIG = int32(5);
SMALL = int32(3);
TARGET = int32(4);
QUICK_TIME = int32(4);

Simulink.defineIntEnumType('t_action', ... 
	{'Fill_small', 'Fill_big', 'Empty_small', 'Empty_big', 'Pour_big_into_small', 'Pour_small_into_big'}, ...
	0:5);
