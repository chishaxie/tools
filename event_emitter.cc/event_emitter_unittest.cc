#include <iostream>

#include "event_emitter.h"

void fun0()
{
	std::cout << "fun0()" << std::endl;
}

void fun1()
{
	std::cout << "fun1()" << std::endl;
}

void fun2(int x)
{
	std::cout << "fun2(" << x << ")" << std::endl;
}

int main()
{
	EventEmitter *poEmitter = new EventEmitter();
	
	poEmitter->emit(1);
	poEmitter->emit(2, 2);
	
	unsigned int a = poEmitter->on(1, std::function<void ()>(fun0));
	unsigned int b = poEmitter->on(1, std::function<void ()>(fun1));
	poEmitter->emit(1);
	
	poEmitter->remove_listener(a);
	poEmitter->emit(1);
	
	poEmitter->remove_listener(b);
	poEmitter->emit(1);
	
	poEmitter->on(2, std::function<void (int)>(fun2));
	poEmitter->emit(2, 2);
	//poEmitter->on(1, std::function<void ()>()); //check error
	//poEmitter->emit(2); //check error
	
	delete poEmitter;
	
	return 0;
}
