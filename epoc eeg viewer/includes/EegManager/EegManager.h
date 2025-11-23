#pragma once

// Standard includes
#include <fstream>
#include <conio.h>
#include <deque>
#include <windows.h>

// Project includes
#include "EegManager/EegManager.h"
#include "DirectSoundManager/DirectSoundManager.h"
#include "WasapiManager/WasapiManager.h"

// Emotiv includes
#include "Emotiv/EmoStateDLL.h"
#include "Emotiv/edk.h"
#include "Emotiv/edkErrorCode.h"
#include <initguid.h>
//DEFINE_GUID(DSDEVID_DefaultPlayback, 0xdef00000, 0x9c6d, 0x47ed, 0xaa, 0xf1, 0x4d, 0xda, 0x8f, 0x2b, 0x5c, 0x03);

// Defines
#define Y_OFFSET 3700

class EegManager
{

public:
	static DWORD WINAPI feedData(LPVOID lpParameter);
	static bool identifyEstimuli();

	static std::deque<double> AF3;
	static unsigned int thresholdEstimuli;
	static unsigned int estimuliCounter;

private:
	static void PreciseSleep(double milliseconds);

	static unsigned long latencyTickStart;
	static EE_DataChannel_t targetChannelList[];
	static unsigned long tick;
	static unsigned int counter;
};

