#include "EegManager/EegManager.h"

#pragma comment(lib, "lib/edk.lib")

std::deque<double> EegManager::AF3;
unsigned long EegManager::latencyTickStart = 0;
EE_DataChannel_t EegManager::targetChannelList[] = {
ED_COUNTER,
ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7,
ED_P7, ED_O1, ED_O2, ED_P8, ED_T8,
ED_FC6, ED_F4, ED_F8, ED_AF4, ED_GYROX, ED_GYROY, ED_TIMESTAMP,
ED_FUNC_ID, ED_FUNC_VALUE, ED_MARKER, ED_SYNC_SIGNAL
};
unsigned int EegManager::thresholdEstimuli = 300;
unsigned long EegManager::tick = 0;
unsigned int EegManager::counter = 0;
unsigned int EegManager::estimuliCounter = 0;

DWORD WINAPI EegManager::feedData(LPVOID lpParameter) 
{
	LARGE_INTEGER current, holder, frequencyTime, start;
	EmoEngineEventHandle eEvent = EE_EmoEngineEventCreate();
	EmoStateHandle eState = EE_EmoStateCreate();
	QueryPerformanceCounter(&start);
	unsigned int userID = 0;
	const unsigned short composerPort = 1726;
	float secs = 1;
	bool readytocollect = false;
	int option = 0;
	int state = 0;
	int frequency = 128;
	double sampleDeltaTimeMs = 7.6f;
	double interval;
	double deltaTime;

	char* fullfilename = "study_wait_wasapi_dsound_1.csv";
	std::ofstream ofs(fullfilename, std::ios::trunc);

	try {
		if (EE_EngineConnect() != EDK_OK) {
			throw std::exception("Emotiv Engine start up failed.");
		}

		DataHandle hData = EE_DataCreate();
		EE_DataSetBufferSizeInSec(secs);

		QueryPerformanceFrequency(&frequencyTime);
		QueryPerformanceCounter(&start);
		QueryPerformanceCounter(&holder);
		while (!_kbhit())
		{
			state = EE_EngineGetNextEvent(eEvent);

			if (state == EDK_OK)
			{
				EE_Event_t eventType = EE_EmoEngineEventGetType(eEvent);
				EE_EmoEngineEventGetUserId(eEvent, &userID);

				// Log the EmoState if it has been updated
				if (eventType == EE_UserAdded) {
					EE_DataAcquisitionEnable(userID, true);
					readytocollect = true;
				}
			}

			if (readytocollect) 
			{

				QueryPerformanceCounter(&current);
				interval = static_cast<double>(current.QuadPart - start.QuadPart) / frequencyTime.QuadPart * 1000;

				EE_DataUpdateHandle(userID, hData);

				unsigned int nSamplesTaken = 0;
				EE_DataGetNumberOfSample(hData, &nSamplesTaken);

				if (nSamplesTaken != 0) 
				{
					double* data = new double[nSamplesTaken];
					double* timestamps = new double[nSamplesTaken];
					//double* sync = new double[nSamplesTaken];
					for (int sampleIdx = 0; sampleIdx < (int)nSamplesTaken; ++sampleIdx)
					{
						EE_DataGet(hData, ED_TIMESTAMP, timestamps, nSamplesTaken);
						ofs << timestamps[sampleIdx]*1000 << ", ";
						
						EE_DataGet(hData, ED_AF3, data, nSamplesTaken);
						//EE_DataGet(hData, ED_SYNC_SIGNAL, sync, nSamplesTaken);

						//if (sync[sampleIdx] == 999)
						//{
						//	ofs << ", " << "S";
						//	EE_DataSetSychronizationSignal(userID, 0);
						//}
						AF3.push_back(data[sampleIdx]);
						ofs << data[sampleIdx];
						//ofs << sync[sampleIdx] << ", ";
						//ofs << sampleIdx;

						if (identifyEstimuli())
						{
							ofs << ", " << "estimuli";
							//ofs << ", " << "R";
							latencyTickStart = tick;
							estimuliCounter++;
							QueryPerformanceCounter(&current);
							deltaTime = static_cast<double>(current.QuadPart - start.QuadPart) / frequencyTime.QuadPart * 1000 - interval;

							double delta = (sampleDeltaTimeMs*sampleIdx - deltaTime) * 1000000;

							holder.QuadPart = current.QuadPart + (delta)*frequencyTime.QuadPart / 1000000000;
							do
							{
								QueryPerformanceCounter(&current);
							} while (current.QuadPart < holder.QuadPart);
							//PreciseSleep(500);
							//WasapiManager::playFlag.store(true);
							DirectSoundManager::playFlag.store(true);

							//EE_DataSetSychronizationSignal(userID, 999);
						}

						ofs << std::endl;
						tick++;
					}
					delete[] data;
					delete[] timestamps;
					//delete[] sync;
				}
			}
		}
		ofs.close();
		EE_DataFree(hData);
	}
	catch (const std::exception& e)
	{
	}

	EE_EngineDisconnect();
	EE_EmoStateFree(eState);
	EE_EmoEngineEventFree(eEvent);

	return 0;
}

bool EegManager::identifyEstimuli()
{
	if (tick < latencyTickStart + 256 + (counter%7))
	{
		return false;
	}

	if (tick > 256 && abs(AF3.back()) < (thresholdEstimuli + Y_OFFSET))
	{
		counter++;
		return true;
	}

	return false;
}

void EegManager::PreciseSleep(double milliseconds)
{
	LARGE_INTEGER freq, start, end;
	QueryPerformanceFrequency(&freq);
	QueryPerformanceCounter(&start);
	end.QuadPart = start.QuadPart + static_cast<LONGLONG>(milliseconds * freq.QuadPart / 1000.0);

	while (true)
	{
		LARGE_INTEGER curr;
		QueryPerformanceCounter(&curr);
		if (curr.QuadPart >= end.QuadPart)
		{
			break;
		}
	}
}