#ifndef __TOP_K_H__
#define __TOP_K_H__

/* top-k 接口 */
template<class T>
class ITopK
{
public:
	virtual bool offer(T element, int incrementCount = 1) = 0;
	virtual int peek(int k, T *outT, long *outCount = NULL) = 0;
	virtual long totalCount() = 0;
	virtual void reset() = 0;
	virtual ~ITopK() = 0;
};

template<class T>
ITopK<T>::~ITopK()
{
	//析构函数必须实现
}

#endif
