#ifndef __STREAM_TOP_K_H__
#define __STREAM_TOP_K_H__

#include <map>
#include <list>
using namespace std;

#include "top-k.h"

template<class T>class StreamTopper; //实现ITopK接口的类

template<class T>class Bucket;
template<class T>class Counter;

/* C++不支持模板别名,坑,以下非主流写法 */
//template<class T> typedef typename list<Bucket<T>*>::iterator BucketListNode<T>;
#define BucketListNode(T) 	typename list<Bucket<T>*>::iterator
#define CounterListNode(T) 	typename list<Counter<T>*>::iterator

template<class T>
class Counter
{
public:
	BucketListNode(T) bucketNode;
	T element;
	long count;
};

template<class T>
class Bucket
{
public:
	Bucket(long count);
public:
	list<Counter<T>*> counterList;
	long count;
};

template<class T>
class StreamTopper: public ITopK<T>
{
public:
	StreamTopper(int capacity);
	~StreamTopper();
	bool offer(T element, int incrementCount = 1);
	int peek(int k, T *outT, long *outCount = NULL);
	long totalCount();
	void reset();
private:
	long count;
	int capacity;
	list<Bucket<T>*> bucketList;
	map<T, CounterListNode(T)> counterMap;
	Counter<T> *_pCounterMem; //Counter只线性分配,自己hold内存
	int _iCurCounterMemNum;
};

template<class T>
Bucket<T>::Bucket(long count)
{
	this->count = count;
}

/* StreamTopper 部分 */

template<class T>
StreamTopper<T>::StreamTopper(int capacity)
{
	this->capacity = capacity;
	this->_iCurCounterMemNum = 0;
	this->_pCounterMem = new Counter<T>[capacity];
}

template<class T>
StreamTopper<T>::~StreamTopper()
{
	for (BucketListNode(T) bNode = this->bucketList.begin(); bNode != this->bucketList.end(); bNode++)
		delete *bNode;
	delete [] this->_pCounterMem;
}

template<class T>
bool StreamTopper<T>::offer(T element, int incrementCount)
{	
	if (incrementCount <= 0)
		return false;
		
	this->count ++;
	
	typename map<T, CounterListNode(T)>::iterator it = this->counterMap.find(element);
	
	CounterListNode(T) counterNode;
	
	if (it == this->counterMap.end())
	{
		if ((int)this->counterMap.size() < this->capacity)
		{
			//生成一个新的桶 放到尾部
			Bucket<T> *cur = new Bucket<T>(0);
			BucketListNode(T) bucketTmpNode = this->bucketList.insert(this->bucketList.end(), cur);
			Counter<T> *newCounter = &this->_pCounterMem[this->_iCurCounterMemNum++];
			newCounter->element = element;
			newCounter->bucketNode = bucketTmpNode;
			newCounter->count = 0;
			counterNode = cur->counterList.insert(cur->counterList.end(), newCounter);
		}
		else
		{
			//找尾部的桶,直接替换
			Bucket<T> *min = this->bucketList.back();
			counterNode = min->counterList.begin(); //覆盖最早进入的
			this->counterMap.erase((*counterNode)->element); //map删除
			(*counterNode)->element = element;
		}
	}
	else
		counterNode = it->second;
		
	BucketListNode(T) bucketNode = (*counterNode)->bucketNode;
	BucketListNode(T) bucketNodeNext = bucketNode;
	
	Counter<T>* counter = *counterNode;
	
	(*bucketNode)->counterList.erase(counterNode);
	
	counter->count += incrementCount;
	
	
	//不是最大,且小于新count
	while (bucketNodeNext != this->bucketList.begin() && counter->count > (*bucketNodeNext)->count)
		bucketNodeNext--;
	
	if ((*bucketNodeNext)->count == counter->count)
		counterNode = (*bucketNodeNext)->counterList.insert((*bucketNodeNext)->counterList.end(), counter);
	else
	{
		//不是最大,又不等于,必然是大于
		if (counter->count < (*bucketNodeNext)->count)
			bucketNodeNext ++;
		
		Bucket<T> *bucketNext = new Bucket<T>(counter->count);
		counterNode = bucketNext->counterList.insert(bucketNext->counterList.end(), counter);
		bucketNodeNext = this->bucketList.insert(bucketNodeNext, bucketNext);
	}
	
	counter->bucketNode = bucketNodeNext;
	
	this->counterMap[element] = counterNode; //无则添加 有则覆盖
	
	if ((*bucketNode)->counterList.empty())
	{
		this->bucketList.erase(bucketNode);
		delete (*bucketNode);
	}
	
	return true;
}

template<class T>
int StreamTopper<T>::peek(int k, T *outT, long *outCount)
{
	int r = 0;
	
	for (BucketListNode(T) bNode = this->bucketList.begin(); bNode != this->bucketList.end(); bNode++)
	{
		for (CounterListNode(T) cNode = (*bNode)->counterList.begin();
			cNode != (*bNode)->counterList.end(); cNode++)
		{
			outT[r] = (*cNode)->element;
			if (outCount)
				outCount[r] = (*bNode)->count;
			r ++;
			if (r == k)
				return r;
		}
	}
	
	return r;
}

template<class T>
long StreamTopper<T>::totalCount()
{
	return this->count;
}

template<class T>
void StreamTopper<T>::reset()
{
	for (BucketListNode(T) bNode = this->bucketList.begin(); bNode != this->bucketList.end(); bNode++)
		delete *bNode;
	this->bucketList.clear();
	this->counterMap.clear();
	this->_iCurCounterMemNum = 0;
	this->count = 0;
}

#endif
