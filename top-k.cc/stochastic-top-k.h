#ifndef __STOCHASTIC_TOP_K_H__
#define __STOCHASTIC_TOP_K_H__

#include <time.h>
#include <stdlib.h>
#include <map>
using namespace std;

#include "top-k.h"

template<class T>class StochasticTopper; //实现ITopK接口的类

template<class T>
class ISampleSet
{
public:
    virtual long put(T element, int incrementCount) = 0;
    virtual T removeRandom() = 0;
    virtual T peek() = 0;
    virtual int peek(int k, T *outT, long *outCount) = 0;
    virtual int size() = 0;
    virtual long count() = 0;
	virtual ~ISampleSet(){}
};

template<class T>
class Node
{
public:
	Node<T> *next;
	Node<T> *prev;
	T element;
	long count;
};

template<class T>
class SampleSet: public ISampleSet<T>
{
public:
	SampleSet();
	~SampleSet();
	long put(T element, int incrementCount);
	T removeRandom();
	T peek();
	int peek(int k, T *outT, long *outCount);
	int size();
	long count();
protected:
	T removeMin();
	void promote(Node<T> *node);
	void demote(Node<T> *node);
private:
	map<T, Node<T>*> sampleMap;
	Node<T> *head;
	Node<T> *tail;
	int _size;
	long _count;
};

template<class T>
class StochasticTopper: public ITopK<T>
{
public:
	StochasticTopper(int sampleSize);
	StochasticTopper(int sampleSize, unsigned int seed);
	~StochasticTopper();
	bool offer(T element, int incrementCount = 1);
	int peek(int k, T *outT, long *outCount = NULL);
	long totalCount();
	void reset();
protected:
	void init(int sampleSize, unsigned int seed);
private:
	int sampleSize;
	ISampleSet<T> *sample;
	long count;
};

/* SampleSet 部分 */

template<class T>
SampleSet<T>::SampleSet()
{
	this->_size = 0;
	this->_count = 0;
	this->head = NULL;
	this->tail = NULL;
}

template<class T>
SampleSet<T>::~SampleSet()
{
	Node<T> *itr = this->head, *tmp;
	while (itr != NULL)
	{
		tmp = itr;
		itr = itr->next;
		delete tmp;
	}
}

template<class T>
long SampleSet<T>::put(T element, int incrementCount)
{
	typename map<T, Node<T>*>::iterator it = this->sampleMap.find(element);
	Node<T> *node = (it != this->sampleMap.end()) ? it->second : NULL;
	if (node)
	{
		node->count += incrementCount;
		promote(node); //该节点位置向前调整
	}
	else
	{
		node = new Node<T>();
		node->element = element;
		node->count = incrementCount;
		node->prev = this->tail;
		node->next = NULL;
		if (this->tail != NULL)
			this->tail->next = node;
		this->tail = node;
		if (this->head == NULL)
			this->head = node;
		this->sampleMap.insert( pair<T, Node<T>*>(element, node) );
		this->_size++;
	}
	this->_count++;
	return node->count;
}

template<class T>
T SampleSet<T>::removeRandom()
{
	double p = (rand()%65536) / 65536.0;
	long weight = 0;
	for (Node<T> *itr = this->head; itr != NULL; itr = itr->next)
	{
		weight += itr->count;
		if (p < weight / (double)this->_count)
		{
			itr->count--;
			this->_count--;
			demote(itr); //该节点位置向后调整
			if (itr->count == 0)
				removeMin();
			return itr->element;
		}
	}
	return T();
}

template<class T>
T SampleSet<T>::peek()
{
	return (this->head != NULL) ? head->element : T();
}

template<class T>
int SampleSet<T>::peek(int k, T *outT, long *outCount)
{
	int r = 0;
	if (outCount)
		for (Node<T> *itr = head; itr != NULL && r < k; itr = itr->next, r++)
		{
			outT[r] = itr->element;
			outCount[r] = itr->count;
		}
	else
		for (Node<T> *itr = head; itr != NULL && r < k; itr = itr->next, r++)
			outT[r] = itr->element;
	return r;
}

template<class T>
int SampleSet<T>::size()
{
	return this->_size;
}

template<class T>
long SampleSet<T>::count()
{
	return this->_count;
}

template<class T>
T SampleSet<T>::removeMin()
{
	if (this->tail == NULL)
		return T();
	this->_size--;
	this->_count -= this->tail->count;
	T minElement = this->tail->element;
	this->tail = this->tail->prev;
	if (this->tail != NULL)
		this->tail->next = NULL;
	typename map<T, Node<T>*>::iterator it = this->sampleMap.find(minElement);
	//Assert(it != this->sampleMap.end())
	delete it->second;
	this->sampleMap.erase(it);
	return minElement;
}

template<class T>
void SampleSet<T>::promote(Node<T> *node)
{
	while (node->prev != NULL && node->count > node->prev->count)
	{
		Node<T> *b = node->prev, *c = node, *d = node->next, *a = (b == NULL) ? NULL : b->prev;
		
		if (a != NULL)
			a->next = c;
		c->prev = a;

		c->next = b;
		b->prev = c;

		b->next = d;
		if (d != NULL)
			d->prev = b;
		
		if (this->head == b)
			this->head = c;
		if (this->tail == c)
			this->tail = b;
	}
}

template<class T>
void SampleSet<T>::demote(Node<T> *node)
{
	while (node->next != NULL && node->count < node->next->count)
	{
		Node<T> *a = node->prev, *b = node, *c = node->next, *d = (c == NULL) ? NULL : c->next;

		if (a != NULL)
			a->next = c;
		c->prev = a;

		c->next = b;
		b->prev = c;

		if (d != NULL)
			d->prev = b;
		b->next = d;

		if (this->head == b)
			this->head = c;
		if (this->tail == c)
			this->tail = b;
	}
}

/* StochasticTopper 部分 */

template<class T>
StochasticTopper<T>::StochasticTopper(int sampleSize)
{
	this->init(sampleSize, (unsigned int)time(NULL));
}

template<class T>
StochasticTopper<T>::StochasticTopper(int sampleSize, unsigned int seed)
{
	this->init(sampleSize, seed);
}

template<class T>
void StochasticTopper<T>::init(int sampleSize, unsigned int seed)
{
	this->sample = new SampleSet<T>();
	this->sampleSize = sampleSize;
	this->count = 0;
	srand(seed);
}

template<class T>
StochasticTopper<T>::~StochasticTopper()
{
	delete this->sample;
}

template<class T>
bool StochasticTopper<T>::offer(T element, int incrementCount)
{
	if (incrementCount <= 0)
		return false;
	
	this->count++;
	bool taken = false;
	if (this->sample->count() < this->sampleSize)
	{
		this->sample->put(element, incrementCount);
		taken = true;
	}
	else if ((rand()%65536) / 65536.0 < this->sampleSize / (double)this->count)
	{
		this->sample->removeRandom();
		this->sample->put(element, incrementCount);
		taken = true;
	}
	return taken;
}

template<class T>
int StochasticTopper<T>::peek(int k, T *outT, long *outCount)
{
	return this->sample->peek(k, outT, outCount);
	/*
	//比率放大
	int r = this->sample->peek(k, outT, outCount);
	int ratio = this->count / this->sample->count();
	if (outCount && r > 0 && ratio > 1)
	{ 
		for (int i=0; i<r; i++)
			outCount[i] = outCount[i] * ratio;
	}
	return r;
	*/
}

template<class T>
long StochasticTopper<T>::totalCount()
{
	return this->count;
}

template<class T>
void StochasticTopper<T>::reset()
{
	delete this->sample;
	this->sample = new SampleSet<T>();
	this->sampleSize = sampleSize;
	this->count = 0;
}

#endif
