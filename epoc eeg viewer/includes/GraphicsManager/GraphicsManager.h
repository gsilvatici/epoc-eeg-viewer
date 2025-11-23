#pragma once

// Standard includes
#include <windows.h>
#include <winuser.h>
#include <gdiplus.h>

class GraphicsManager
{
public:
	static void draw(HDC hdc);
	static void drawLineEvent(HDC hdc);
	static void drawLineEvent(HDC hdc, unsigned int tick);
	static void eraseThresholdLine(HDC hdc, unsigned int Y);

	static unsigned int WINDOW_WIDTH;
	static unsigned int WINDOW_HEIGHT;
private:
	static unsigned long drawTick;
};

