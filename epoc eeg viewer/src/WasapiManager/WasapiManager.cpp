//#include "WasapiManager/WasapiManager.h"

//void WasapiManager::init()
//{
//	void* fileBytes;
//	uint32_t fileSize;
//	bool result = loadRawFile("512hz.wav", &fileBytes, &fileSize);
//
//	WavFile* wav = (WavFile*)fileBytes;
//	uint32_t numWavSamples = wav->dataChunkSize / (wav->numChannels * sizeof(uint16_t));
//	uint16_t* wavSamples = &wav->samples;
//
//	HRESULT hr = CoInitializeEx(nullptr, COINIT_SPEED_OVER_MEMORY);
//
//	IMMDeviceEnumerator* deviceEnumerator;
//	hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), (LPVOID*)(&deviceEnumerator));
//
//	IMMDevice* audioDevice;
//	hr = deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &audioDevice);
//
//	deviceEnumerator->Release();
//
//	IAudioClient2* audioClient;
//	hr = audioDevice->Activate(__uuidof(IAudioClient2), CLSCTX_ALL, nullptr, (LPVOID*)(&audioClient));
//
//	audioDevice->Release();
//
//	WAVEFORMATEX mixFormat = {};
//	mixFormat.wFormatTag = WAVE_FORMAT_PCM;
//	mixFormat.nChannels = 2;
//	mixFormat.nSamplesPerSec = 44100;//defaultMixFormat->nSamplesPerSec;
//	mixFormat.wBitsPerSample = 16;
//	mixFormat.nBlockAlign = (mixFormat.nChannels * mixFormat.wBitsPerSample) / 8;
//	mixFormat.nAvgBytesPerSec = mixFormat.nSamplesPerSec * mixFormat.nBlockAlign;
//
//	const int64_t REFTIMES_PER_SEC = 10000000; // hundred nanoseconds
//	REFERENCE_TIME requestedSoundBufferDuration = REFTIMES_PER_SEC * 2;
//	DWORD initStreamFlags = (AUDCLNT_STREAMFLAGS_RATEADJUST
//		| AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM
//		| AUDCLNT_STREAMFLAGS_SRC_DEFAULT_QUALITY);
//	hr = audioClient->Initialize(AUDCLNT_SHAREMODE_SHARED,
//		initStreamFlags,
//		requestedSoundBufferDuration,
//		0, &mixFormat, nullptr);
//
//	IAudioRenderClient* audioRenderClient;
//	hr = audioClient->GetService(__uuidof(IAudioRenderClient), (LPVOID*)(&audioRenderClient));
//
//	UINT32 bufferSizeInFrames;
//	hr = audioClient->GetBufferSize(&bufferSizeInFrames);
//
//	hr = audioClient->Start();
//
//
//	int wavPlaybackSample = 0;
//	while (true)
//	{
//		UINT32 bufferPadding;
//		hr = audioClient->GetCurrentPadding(&bufferPadding);
//
//		UINT32 soundBufferLatency = bufferSizeInFrames / 50;
//		UINT32 numFramesToWrite = soundBufferLatency - bufferPadding;
//
//		int16_t* buffer;
//		hr = audioRenderClient->GetBuffer(numFramesToWrite, (BYTE**)(&buffer));
//
//		for (UINT32 frameIndex = 0; frameIndex < numFramesToWrite; ++frameIndex)
//		{
//			*buffer++ = wavSamples[wavPlaybackSample]; // left
//			*buffer++ = wavSamples[wavPlaybackSample]; // right
//
//			++wavPlaybackSample;
//			wavPlaybackSample %= numWavSamples;
//		}
//		hr = audioRenderClient->ReleaseBuffer(numFramesToWrite, 0);
//
//	}
//
//}
//
//bool WasapiManager::loadRawFile(char* filename, void** data, uint32_t* numBytesRead)
//{
//	HANDLE file = CreateFileA(filename, GENERIC_READ, 0, 0, OPEN_EXISTING, 0, 0);
//	if ((file == INVALID_HANDLE_VALUE)) return false;
//
//	DWORD fileSize = GetFileSize(file, 0);
//	if (!fileSize) return false;
//
//	*data = HeapAlloc(GetProcessHeap(), 0, fileSize + 1);
//	if (!*data) return false;
//
//	if (!ReadFile(file, *data, fileSize, (LPDWORD)numBytesRead, 0))
//		return false;
//
//	CloseHandle(file);
//	((uint8_t*)*data)[fileSize] = 0;
//
//	return true;
//}
//
//void WasapiManager::playSound()
//{
//	//PlaySound(TEXT("16hz.wav"), NULL, SND_FILENAME);
//	//buffer->Play(0, 0, 0);
//}
//
//
//DWORD WINAPI WasapiManager::pl(LPVOID lpParameter)
//{
//	init();
//	return 0;
//}

#include "WasapiManager/WasapiManager.h"

// Libs
#pragma comment(lib, "Avrt.lib")

HANDLE WasapiManager::eventHandle;

// audio format = 44.1khz 16bit stereo
const int32_t WasapiManager::sampleSize = 2;
const int32_t WasapiManager::channelCount = 2;
const int32_t WasapiManager::sampleRate = 44100;
const int32_t WasapiManager::frameSize = sampleSize * channelCount;

// user input / audio thread communication
std::atomic_bool WasapiManager::stopFinished;
std::atomic_bool WasapiManager::stopInitiated;
std::atomic_bool WasapiManager::playFlag;

// sample data
int16_t* WasapiManager::wavDataSamples;
size_t WasapiManager::wavDataSampleCount;
std::vector<char> WasapiManager::wavDataRaw;
char const* WasapiManager::wavFilePath = "16hzB.wav";

WasapiManager::AudioThreadData WasapiManager::data;

WAVEFORMATEXTENSIBLE WasapiManager::makeAudioFormat()
{
    // translate format specification to WAVEFORMATEXTENSIBLE
    WAVEFORMATEXTENSIBLE result = { 0 };
    result.dwChannelMask = 0;
    result.SubFormat = KSDATAFORMAT_SUBTYPE_PCM;
    result.Samples.wValidBitsPerSample = sampleSize * 8;
    result.Format.nChannels = channelCount;
    result.Format.nSamplesPerSec = sampleRate;
    result.Format.wBitsPerSample = sampleSize * 8;
    result.Format.wFormatTag = WAVE_FORMAT_EXTENSIBLE;
    result.Format.cbSize = sizeof(WAVEFORMATEXTENSIBLE);
    result.Format.nBlockAlign = channelCount * sampleSize;
    result.Format.nAvgBytesPerSec = channelCount * sampleSize * sampleRate;
    return result;
}

void WasapiManager::loadWavFile()
{
    // load piano samples to bytes
    auto path = wavFilePath;
    std::ifstream input(path, std::ios::binary);
    assert(input);
    input.seekg(0, input.end);
    size_t length = input.tellg();
    input.seekg(0, input.beg);
    wavDataRaw.reserve(length);
    input.read(wavDataRaw.data(), length);
    assert(input);
    input.close();

    // compute frame count and set actual audio data
    // 44 bytes skipped for .WAV file header
    wavDataSampleCount = (length - 44) / (sampleSize * channelCount);
    wavDataSamples = reinterpret_cast<int16_t*>(wavDataRaw.data() + 44);
}

void WasapiManager::init()
{
    int32_t chr;
    BOOL success;
    UINT32 bufferFrames;
    REFERENCE_TIME engine;
    REFERENCE_TIME period;
    CComPtr<IMMDevice> device;
    CComPtr<IMMDeviceEnumerator> enumerator;
    WAVEFORMATEXTENSIBLE format = makeAudioFormat();

    loadWavFile();

    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

    // exclusive mode event driven must use 128-byte aligned buffers
    const int32_t alignment_requirement_bytes = 128;

    // timing stuff
    const int64_t millisPerSecond = 1000;
    const int64_t reftimesPerMilli = 10000;

    // get default render endpoint
    CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator), reinterpret_cast<void**>(&enumerator));
    enumerator->GetDefaultAudioEndpoint(eRender, eMultimedia, &device);
    device->Activate(__uuidof(IAudioClient), CLSCTX_ALL,
        nullptr, reinterpret_cast<void**>(&data.client));

    // open exclusive mode event driven stream
    data.client->GetDevicePeriod(&engine, &period);
    bufferFrames = static_cast<uint32_t>(period / reftimesPerMilli * sampleRate / millisPerSecond);
    while ((bufferFrames * frameSize) % alignment_requirement_bytes != 0) bufferFrames++;
    period = bufferFrames * millisPerSecond * reftimesPerMilli / sampleRate;
    data.client->Initialize(AUDCLNT_SHAREMODE_EXCLUSIVE, AUDCLNT_STREAMFLAGS_EVENTCALLBACK,
        period, period, reinterpret_cast<WAVEFORMATEX*>(&format), nullptr);
    eventHandle = CreateEvent(nullptr, FALSE, FALSE, nullptr);
    assert(eventHandle != nullptr);
    data.client->SetEventHandle(eventHandle);
    data.client->GetService(__uuidof(IAudioClock), reinterpret_cast<void**>(&data.clock));
    data.client->GetService(__uuidof(IAudioRenderClient), reinterpret_cast<void**>(&data.render));

    CreateThread(nullptr, 0, runAudioThread, nullptr, 0, nullptr);


    //playFlag.store(true);

    // cleanup
    //stopInitiated.store(true);
    //while (!stopFinished.load());
    //success = CloseHandle(eventHandle);
    //assert(success);
}

DWORD WINAPI WasapiManager::runAudioThread(void* param)
{
    int16_t* audio;
    BYTE* audio_mem;
    UINT32 bufferFrames;

    HANDLE task;
    BOOL success;
    DWORD waitResult;
    DWORD taskIndex = 0;

    // init thread
    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    task = AvSetMmThreadCharacteristicsW(TEXT(L"Pro Audio"), &taskIndex);
    assert(task != nullptr);

    data.client->GetBufferSize(&bufferFrames);

    size_t frame_index = 0;
    bool play = false;

    // audio loop
    data.client->Start();
    while (!stopInitiated.load())
    {
        waitResult = WaitForSingleObject(eventHandle, INFINITE);
        assert(waitResult == WAIT_OBJECT_0);

        // retrieve and clear buffer for this round
        data.render->GetBuffer(bufferFrames, &audio_mem);
        audio = reinterpret_cast<int16_t*>(audio_mem);
        memset(audio, 0, bufferFrames * static_cast<uint64_t>(frameSize));

        if (playFlag.load())
        {
            frame_index = 0;
            play = true;
            playFlag.store(false);
        }

        if (play)
        {
            for (size_t f = 0; f < bufferFrames; f++)
            {
                if (frame_index < wavDataSampleCount)
                {
                    for (size_t c = 0; c < channelCount; c++)
                    {
                        audio[f * channelCount + c] = wavDataSamples[frame_index * channelCount + c];
                    }
                    frame_index++;
                }
                else
                {
                    play = false;
                    break;
                }
            }
        }

        data.render->ReleaseBuffer(bufferFrames, 0);
    }
    data.client->Stop();

    // cleanup
    success = AvRevertMmThreadCharacteristics(task);
    assert(success);
    CoUninitialize();
    stopFinished.store(true);
    return 0;
}
