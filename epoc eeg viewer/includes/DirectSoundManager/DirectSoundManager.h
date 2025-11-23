#pragma once

// Standard includes
#include <vector>
#include <iostream>
#include <fstream>

// DirectSound includes
#include <dsound.h>
DEFINE_GUID(DSDEVID_DefaultPlayback, 0xdef00000, 0x9c6d, 0x47ed, 0xaa, 0xf1, 0x4d, 0xda, 0x8f, 0x2b, 0x5c, 0x03);

class DirectSoundManager
{
	struct WavHeader 
	{
		char chunkID[4];
		unsigned int chunkSize;
		char format[4];
		char subchunk1ID[4];
		unsigned int subchunk1Size;
		unsigned short audioFormat;
		unsigned short numChannels;
		unsigned int sampleRate;
		unsigned int byteRate;
		unsigned short blockAlign;
		unsigned short bitsPerSample;
	};
public:
	static void init(HWND hwn);
	static std::vector<BYTE> loadWavFile(const std::string& filename, WavHeader& outHeader);
	static DWORD WINAPI playSound(LPVOID lpParameter);

	static std::atomic_bool playFlag;
private:
	static LPDIRECTSOUNDBUFFER buffer;
};

