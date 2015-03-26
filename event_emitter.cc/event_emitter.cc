#include "event_emitter.h"

EventEmitter::EventEmitter()
	: m_iLastListenerId(0)
{
}

EventEmitter::~EventEmitter()
{
	for (ListenersIterator it = this->m_mapListeners.begin(); it != this->m_mapListeners.end(); it++)
		delete it->second;
}

void EventEmitter::remove_listener(unsigned int iListenerId)
{
	std::map<unsigned int, ListenersIterator>::iterator it = this->m_mapId2Listener.find(iListenerId);
	if (it != this->m_mapId2Listener.end())
	{
		delete it->second->second;
		this->m_mapListeners.erase(it->second);
	}
}
