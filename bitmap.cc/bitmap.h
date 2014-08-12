/*
 *
 * Demo:
 *
 * Bitmap<int> bm(-100, 1000);
 * bm.set(); //Set all true
 * bm[-1] = bm[2] = false;
 * Assert( !bm[2] );
 *
 */
#ifndef __BITMAP_H__
#define __BITMAP_H__

#include <stdlib.h>
#include <string.h>

#include <limits>

template<class T>
class Bitmap
{
public:
	Bitmap(T tMin = std::numeric_limits<T>::min(), T tMax = std::numeric_limits<T>::max(),
		void *pMem = NULL, size_t uMemSize = 0)
		:m_tMin(tMin), m_tMax(tMax)
	{
		if (tMin > tMax)
			throw -1;
		this->m_tSize = (size_t)(((tMax - tMin) >> 3) + 1);
		if (uMemSize > 0)
		{
			if (!pMem)
				throw -2;
			if (uMemSize < this->m_tSize)
				throw -3;
		}
		if (!pMem)
		{
			this->m_pMem = new unsigned char[this->m_tSize];
			this->m_bNeedDelete = true;
		}
		else
		{
			this->m_pMem = (unsigned char *)pMem;
			this->m_bNeedDelete = false;
		}
	}
	
	~Bitmap()
	{
		if (this->m_bNeedDelete)
			delete [] this->m_pMem;
	}
	
	class BitmapReference
	{
		friend class Bitmap<T>;
	public:
		operator bool() const
		{
			return this->m_pBitmap->get(this->m_tX);
		}
		bool operator~() const
		{
			return (!this->m_pBitmap->get(this->m_tX));
		}
		BitmapReference& operator=(bool v)
		{
			this->m_pBitmap->set(this->m_tX, v);
			return (*this);
		}
		BitmapReference& operator=(const BitmapReference& other)
		{
			this->m_pBitmap->set(this->m_tX, bool(other));
			return (*this);
		}
		BitmapReference& flip()
		{
			this->m_pBitmap->flip(this->m_tX);
			return (*this);
		}
	private:
		BitmapReference(Bitmap<T>* pBitmap, T x):m_pBitmap(pBitmap), m_tX(x) {}
		BitmapReference(const BitmapReference& other);
		Bitmap<T> *m_pBitmap;
		T m_tX;
	};
	
	bool operator[](T x) const
	{
		return this->get(x);
	}
	
	BitmapReference operator[](T x)
	{
		return BitmapReference(this, x);
	}
	
	Bitmap<T>& set()
	{
		memset(this->m_pMem, 0xff, this->m_tSize);
		return (*this);
	}
	
	Bitmap<T>& reset()
	{
		memset(this->m_pMem, 0, this->m_tSize);
		return (*this);
	}
	
	Bitmap<T>& flip()
	{
		for (size_t i = 0; i < this->m_tSize; i ++)
			this->m_pMem[i] = ~this->m_pMem[i];
		return (*this);
	}
	
	size_t count() const
	{
		return (size_t)(this->m_tMax - this->m_tMin + 1);
	}
	
	size_t size() const
	{
		return this->m_tSize;
	}
	
	T min() const
	{
		return this->m_tMin;
	}
	
	T max() const
	{
		return this->m_tMax;
	}
	
	bool get(T x) const
	{
		if (x < this->m_tMin || x > this->m_tMax)
			throw -4;
		T _x = x - this->m_tMin;
		return ( (this->m_pMem[_x >> 3] & ((unsigned char)1 << (_x & 0x7))) != 0 );
	}
	
	Bitmap<T>& set(T x, bool v = true)
	{
		if (x < this->m_tMin || x > this->m_tMax)
			throw -4;
		T _x = x - this->m_tMin;
		if (v)
			this->m_pMem[_x >> 3] |= ((unsigned char)1 << (_x & 0x7));
		else
			this->m_pMem[_x >> 3] &= ~((unsigned char)1 << (_x & 0x7));
		return (*this);
	}
	
	Bitmap<T>& flip(T x)
	{
		if (x < this->m_tMin || x > this->m_tMax)
			throw -4;
		T _x = x - this->m_tMin;
		this->m_pMem[_x >> 3] ^= ((unsigned char)1 << (_x & 0x7));
		return (*this);
	}
	
private:
	Bitmap(const Bitmap<T>& other);
	Bitmap<T>& operator=(const Bitmap<T>& other);
	unsigned char *m_pMem;
	T m_tMin;
	T m_tMax;
	size_t m_tSize;
	bool m_bNeedDelete;
};

#endif
