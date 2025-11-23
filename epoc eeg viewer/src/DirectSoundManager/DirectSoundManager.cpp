#include "DirectSoundManager/DirectSoundManager.h"

// Statics libs
#pragma comment(lib, "dsound.lib")
#pragma comment(lib, "Winmm.lib")


LPDIRECTSOUNDBUFFER DirectSoundManager::buffer;
std::atomic_bool DirectSoundManager::playFlag;

void DirectSoundManager::init(HWND hwn)
{
	LPDIRECTSOUND8 dsound;
	DirectSoundCreate8(NULL, &dsound, NULL);
	dsound->SetCooperativeLevel(hwn, DSSCL_PRIORITY);

	WavHeader header;
	std::vector<BYTE> wavData = loadWavFile("16hz.wav", header);

	WAVEFORMATEX waveFormat;
	ZeroMemory(&waveFormat, sizeof(WAVEFORMATEX));

	waveFormat.wFormatTag = header.audioFormat;
	waveFormat.nChannels = header.numChannels;
	waveFormat.nSamplesPerSec = header.sampleRate;
	waveFormat.wBitsPerSample = header.bitsPerSample;
	waveFormat.nBlockAlign = header.blockAlign;
	waveFormat.nAvgBytesPerSec = header.byteRate;

	DSBUFFERDESC dsbdesc;
	ZeroMemory(&dsbdesc, sizeof(DSBUFFERDESC));
	dsbdesc.dwSize = sizeof(DSBUFFERDESC);
	dsbdesc.dwFlags = DSBCAPS_STATIC;
	dsbdesc.dwBufferBytes = wavData.size();
	dsbdesc.lpwfxFormat = &waveFormat;

	dsound->CreateSoundBuffer(&dsbdesc, &buffer, NULL);

	VOID* pAudio1 = NULL, * pAudio2 = NULL;
	DWORD audioLength1 = 0, audioLength2 = 0;

	buffer->Lock(0, wavData.size(), &pAudio1, &audioLength1, &pAudio2, &audioLength2, 0);
	memcpy(pAudio1, wavData.data(), audioLength1);

	if (pAudio2 != NULL)
	{
		memcpy(pAudio2, wavData.data() + audioLength1, audioLength2);
	}

	buffer->Unlock(pAudio1, audioLength1, pAudio2, audioLength2);


	buffer->Play(0, 0, 0);

	CreateThread(nullptr, 0, playSound, nullptr, 0, nullptr);
}

std::vector<BYTE> DirectSoundManager::loadWavFile(const std::string& filename, WavHeader& outHeader)
{
	std::ifstream file(filename, std::ios::binary);
	if (!file.is_open())
	{
		std::cerr << "Failed to open WAV file!" << std::endl;
		return {};
	}

	// Read WAV header
	file.read(reinterpret_cast<char*>(&outHeader), sizeof(WavHeader));

	// Simple check to ensure this is a WAV file
	if (strncmp(outHeader.chunkID, "RIFF", 4) != 0 ||
		strncmp(outHeader.format, "WAVE", 4) != 0)
	{
		std::cerr << "Not a valid WAV file!" << std::endl;
		return {};
	}

	// Read WAV data
	std::vector<BYTE> wavData(outHeader.chunkSize - 36); // 36 bytes for the header
	file.read(reinterpret_cast<char*>(wavData.data()), wavData.size());

	return wavData;
}

void PreciseSleep(double milliseconds)
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
#include <Windows.h>

DWORD WINAPI DirectSoundManager::playSound(LPVOID lpParameter)
{
	while (true)
	{
		if (playFlag.load())
		{
			//PreciseSleep(500);
			//PlaySound(TEXT("16hz.wav"), NULL, SND_FILENAME);
			buffer->Play(0, 0, 0);
			playFlag.store(false);
		}
	}
}