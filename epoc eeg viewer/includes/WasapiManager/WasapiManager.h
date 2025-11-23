// Standard includes
#include <atomic>
#include <cstdint>
#include <cassert>
#include <fstream>
#include <iostream>
#include <filesystem>
#include <conio.h>
#include <atlbase.h>
#include <vector>
#include <Windows.h>

// WASAPI includes
#include <avrt.h>
#include <mmdeviceapi.h>
#include <Audioclient.h>
#include <Mmdeviceapi.h>

class WasapiManager
{
	// shared by user input / audio thread
	struct AudioThreadData
	{
		IAudioClock* clock;
		IAudioClient* client;
		IAudioRenderClient* render;
	};

public:
	static void init();
	static DWORD WINAPI runAudioThread(void* param);

	static std::atomic_bool playFlag;

private:
	static WAVEFORMATEXTENSIBLE makeAudioFormat();
	static void loadWavFile();

	static HANDLE eventHandle;

	// audio format = 44.1khz 16bit stereo
	static const int32_t sampleSize;
	static const int32_t channelCount;
	static const int32_t sampleRate;
	static const int32_t frameSize;

	// user input / audio thread communication
	static std::atomic_bool stopFinished;
	static std::atomic_bool stopInitiated;

	// sample data
	static int16_t* wavDataSamples;
	static size_t wavDataSampleCount;
	static std::vector<char> wavDataRaw;
	static char const* wavFilePath;

	static AudioThreadData data;
};