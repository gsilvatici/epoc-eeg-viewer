/**
** EEG Emotiv signal render : Capture EEG info ONLINE from Emotiv and render signals through windows graphic API.

** This program is a modification of epoceeg repository from rramele.
**
** Rodrigo Ramele @ CiC Lab @ ITBA!
**
** Gabriel Silvatici
**/

// Standard includes
#include <windows.h>
#include <winuser.h>
#include <gdiplus.h>
#include <string>

// Project includes
#include "EegManager/EegManager.h"
#include "GraphicsManager/GraphicsManager.h"

// Typedefs
typedef BOOL(WINAPI* PGNSI)(int); // function call for direct to dll

// Defines
#define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 0xfffffffc // select for highest DPI 
#define	PATH	".\\Data\\%s\\%s"

// Using namespace
using namespace Gdiplus;
using namespace std;

HDC hdc;

// Function declaration
LRESULT CALLBACK WindowProcessMessages(HWND hwnd, UINT msg, WPARAM param, LPARAM lparam);

int WINAPI WinMain(HINSTANCE currentInstance, HINSTANCE previousInstance, PSTR cmdLine, INT cmdCount)
{
	// Initialize GDI+
	Gdiplus::GdiplusStartupInput gdiplusStartupInput;
	ULONG_PTR gdiplusToken;
	Gdiplus::GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, nullptr);

	// Register the window class
	const char *CLASS_NAME = "EEG Signal Viewer";
	WNDCLASS wc{};
	wc.hInstance = currentInstance;
	wc.lpszClassName = CLASS_NAME;
	wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
	wc.hbrBackground = (HBRUSH)CreateSolidBrush(RGB(255, 255, 255)); 
	wc.lpfnWndProc = WindowProcessMessages;
	RegisterClass(&wc);

	// Turn off scaling. The following call gets around the lack of a declaration in mingw
	auto pGNSI = (PGNSI)GetProcAddress(GetModuleHandle(TEXT("user32.dll")),
		"SetProcessDpiAwarenessContext");
	if (NULL != pGNSI)
	{
		auto r = pGNSI(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
	}
	HWND hwn = CreateWindow(CLASS_NAME, "EEG Signal Viewer",
		WS_OVERLAPPEDWINDOW | WS_VISIBLE,
		CW_USEDEFAULT, CW_USEDEFAULT,
		GraphicsManager::WINDOW_WIDTH, GraphicsManager::WINDOW_HEIGHT,
		nullptr, nullptr, nullptr, nullptr);

	DirectSoundManager::init(hwn);
	//WasapiManager::init();

	// Create and start thread to feed and persist eeg real time data.
	HANDLE hThread = CreateThread(
		NULL,    
		0,       
		EegManager::feedData,
		NULL,    
		0,       
		NULL);   
	if (hThread == NULL)
	{
		return 1;
	}

	MSG msg{};
	while (GetMessage(&msg, nullptr, 0, 0))
	{
		TranslateMessage(&msg);
		DispatchMessage(&msg);
	}

	
	WaitForSingleObject(hThread, INFINITE);

	CloseHandle(hThread);

	Gdiplus::GdiplusShutdown(gdiplusToken);
	return 0;
}

LRESULT CALLBACK WindowProcessMessages(HWND hwnd, UINT msg, WPARAM param, LPARAM lparam)
{
	int idTimer = -1;
	PAINTSTRUCT ps;
	RECT rc;

	switch (msg) {

	case WM_CREATE:
		// Calculate the starting point.  
		GetClientRect(hwnd, &rc);

		// Initialize the private DC.  
		hdc = GetDC(hwnd);
		SetROP2(hdc, R2_NOT);

		// Start the timer.  
		SetTimer(hwnd, idTimer = 1, 5, NULL);
		return 0L;

	case WM_TIMER:

		RECT rect;
		if (GetWindowRect(hwnd, &rect))
		{
			GraphicsManager::WINDOW_WIDTH = rect.right - rect.left;
			GraphicsManager::WINDOW_HEIGHT = rect.bottom - rect.top;
		}
		BeginPaint(hwnd, &ps);
		GraphicsManager::draw(hdc);
		EndPaint(hwnd, &ps);
		return 0L;

	case WM_DESTROY:
		PostQuitMessage(0);
		return 0L;

	case WM_KEYDOWN:
	{

		switch (param)
		{
		case VK_LEFT: // Left arrow key;
			break;

		case VK_RIGHT: // Right arrow key
			break;

		case VK_UP: // Up arrow key
			GraphicsManager::eraseThresholdLine(hdc, EegManager::thresholdEstimuli);
			EegManager::thresholdEstimuli -= 5;
			break;

		case VK_DOWN: // Down arrow key
			GraphicsManager::eraseThresholdLine(hdc, EegManager::thresholdEstimuli);
			EegManager::thresholdEstimuli += 5;
			break;

		default:
			break;
		}
		return 0L;
	}
	default:
		return DefWindowProc(hwnd, msg, param, lparam);
	}
}
