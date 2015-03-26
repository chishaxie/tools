#ifndef _EVENT_EMITTER_H_
#define _EVENT_EMITTER_H_

#include <stdio.h>
#include <stdlib.h>
#include <map>
#include <functional>

class EventEmitter
{
public:
	EventEmitter();
	~EventEmitter();
	
	template<typename... Args>
	unsigned int add_listener(unsigned int iEventId, std::function<void (Args...)> pfnCallback);
	
	template<typename... Args>
	unsigned int on(unsigned int iEventId, std::function<void (Args...)> pfnCallback);
	
	void remove_listener(unsigned int iListenerId);
	
	template<typename... Args>
	void emit(unsigned int iEventId, Args... args);

private:
	struct ListenerBase
	{
		ListenerBase(unsigned int iListenerId) : m_iListenerId(iListenerId) {}
		virtual ~ListenerBase() {}
		unsigned int m_iListenerId;
	};
	
	template<typename... Args>
	struct Listener : public ListenerBase
	{
		Listener(unsigned int iListenerId, std::function<void (Args...)> pfnCallback)
			: ListenerBase(iListenerId), m_pfnCallback(pfnCallback) {}
		virtual ~Listener() {}
		std::function<void (Args...)> m_pfnCallback;
	};
	
	EventEmitter(const EventEmitter&);
	EventEmitter& operator=(const EventEmitter&);
	
	typedef std::multimap<unsigned int, ListenerBase *>::iterator ListenersIterator;
	
	unsigned int m_iLastListenerId;
	std::multimap<unsigned int, ListenerBase *> m_mapListeners;
	std::map<unsigned int, ListenersIterator> m_mapId2Listener;
};

template<typename... Args>
unsigned int EventEmitter::add_listener(unsigned int iEventId, std::function<void (Args...)> pfnCallback)
{
	if (!pfnCallback)
	{
		fprintf(stderr, "EventEmitter::add_listener(%u, pfnCallback) got an empty pfnCallback.\n", iEventId);
		abort();
	}
	
	unsigned int iListenerId = ++this->m_iLastListenerId;
	
	ListenersIterator it = this->m_mapListeners.insert(std::make_pair(iEventId, new Listener<Args...>(iListenerId, pfnCallback)));
	this->m_mapId2Listener.insert(std::make_pair(iListenerId, it));
	
	return iListenerId;
}

template<typename... Args>
unsigned int EventEmitter::on(unsigned int iEventId, std::function<void (Args...)> pfnCallback)
{
	return this->add_listener(iEventId, pfnCallback);
}

template<typename... Args>
void EventEmitter::emit(unsigned int iEventId, Args... args)
{
	std::pair<ListenersIterator, ListenersIterator> pRet = this->m_mapListeners.equal_range(iEventId);
	for (ListenersIterator it = pRet.first; it != pRet.second; it++)
	{
		Listener<Args...> *poListener = dynamic_cast<Listener<Args...> *>(it->second);
		if (poListener)
			poListener->m_pfnCallback(args...);
		else
		{
			fprintf(stderr, "EventEmitter::emit(%u, ...) match args fails.\n", iEventId);
			abort();
		}
	}
}

#endif //_EVENT_EMITTER_H_
