#include "GraphicsManager/GraphicsManager.h"

// Project includes
#include "EegManager/EegManager.h"

// Using namespace
using namespace Gdiplus;

unsigned int GraphicsManager::WINDOW_WIDTH = 1600;
unsigned int GraphicsManager::WINDOW_HEIGHT = 900;

unsigned long GraphicsManager::drawTick = 0;


void GraphicsManager::draw(HDC hdc)
{
	//std::unique_lock<std::mutex> lock(mu);

	FontFamily  fontFamily(L"Verdana");
	Font        font(&fontFamily, 32, FontStyleRegular, UnitPixel);
	PointF      pointAF3(30.0f, 30.0f);
	PointF      pointCount(GraphicsManager::WINDOW_WIDTH -500.0f, 30.0f);
	SolidBrush  AF3Color(Color(255, 73, 81, 106));

	Gdiplus::Graphics gf(hdc);

	Gdiplus::Pen pen(Gdiplus::Color(255, 73, 81, 106));
	pen.SetWidth(2);

	int y1;
	int y2;
	while (EegManager::AF3.size() > 1)
	{
		//gf.DrawString(L"ESTIMULI# " + std::to_wstring(EegManager::estimuliCounter), -1, &font, pointCouunt, &AF3Color);
		std::wstring estText = L"ESTIMULI# " + std::to_wstring(EegManager::estimuliCounter);
		gf.DrawString(estText.c_str(), -1, &font, pointCount, &AF3Color);


		y1 = (int)EegManager::AF3.front();
		EegManager::AF3.pop_front();
		y2 = (int)EegManager::AF3.front();

		gf.DrawLine(&pen, drawTick, y1 - Y_OFFSET, (drawTick + 2), y2 - Y_OFFSET);

		Gdiplus::Pen pen(Gdiplus::Color(255, 170, 120, 50));
		Gdiplus::Pen erasePen(Gdiplus::Color(255, 255, 255, 255));
		pen.SetWidth(2);
		erasePen.SetWidth(2);

		gf.DrawLine(&pen, 0, EegManager::thresholdEstimuli, WINDOW_WIDTH, EegManager::thresholdEstimuli);

		if (drawTick >= WINDOW_WIDTH)
			drawTick = 0;

		if (drawTick == 0)
		{
			Gdiplus::SolidBrush whiteBrush(Color(255, 255, 255, 255));
			Gdiplus::RectF fillRect(0, 0, (float)(WINDOW_WIDTH - 1), (float)(WINDOW_HEIGHT - 1));
			gf.FillRectangle(&whiteBrush, fillRect);

			// Draw labels
			//FontFamily  fontFamily(L"Verdana");
			//Font        font(&fontFamily, 32, FontStyleRegular, UnitPixel);
			//PointF      pointAF3(30.0f, 30.0f);
			//SolidBrush  AF3Color(Color(255, 73, 81, 106));

			gf.DrawString(L"AF3", -1, &font, pointAF3, &AF3Color);
		}

		drawTick++;
		drawTick++;
	}

}

void GraphicsManager::drawLineEvent(HDC hdc)
{
	//std::unique_lock<std::mutex> lock(mu);
	Gdiplus::Graphics gf(hdc);
	Gdiplus::Pen pen(Gdiplus::Color(255, 170, 120, 50));
	pen.SetWidth(5);
	gf.DrawLine(&pen, drawTick, 0, drawTick, WINDOW_HEIGHT);
}

void GraphicsManager::drawLineEvent(HDC hdc, unsigned int tick)
{
	//std::unique_lock<std::mutex> lock(mu);
	Gdiplus::Graphics gf(hdc);
	Gdiplus::Pen pen(Gdiplus::Color(255, 170, 120, 50));
	pen.SetWidth(5);
	gf.DrawLine(&pen, drawTick, 0, tick, WINDOW_HEIGHT);
}

void GraphicsManager::eraseThresholdLine(HDC hdc, unsigned int Y)
{
	//std::unique_lock<std::mutex> lock(mu);
	Gdiplus::Graphics gf(hdc);
	Gdiplus::Pen pen(Gdiplus::Color(255, 255, 255, 255));
	pen.SetWidth(5);
	gf.DrawLine(&pen, 0, Y, WINDOW_WIDTH, Y);


	//std::unique_lock<std::mutex> lock(mu);
	//Gdiplus::Graphics gf(hdc);
	//Gdiplus::Pen erasePen(Gdiplus::Color(255, 255, 255, 255));
	//Gdiplus::Pen signalPen(Gdiplus::Color(255, 73, 81, 106));

	//erasePen.SetWidth(5);
	////gf.DrawLine(&erasePen, 0, Y, WINDOW_WIDTH, Y);

	//// Create a Bitmap using the current Graphics object
	//Gdiplus::Bitmap bitmap(WINDOW_WIDTH, WINDOW_HEIGHT, &gf);
	//gf.DrawImage(&bitmap, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);

	//// Loop through the X axis to check and repaint pixels
	//for (int x = 0; x < WINDOW_WIDTH; x++)
	//{
	//	Gdiplus::Color pixelColor;
	//	bitmap.GetPixel(x, Y, &pixelColor);

	//	if (pixelColor.GetValue() == Gdiplus::Color(255, 73, 81, 106).GetValue())
	//	{
	//		// Repaint that pixel with the signal color
	//		Gdiplus::SolidBrush signalBrush(Gdiplus::Color(255, 73, 81, 106));
	//		gf.FillRectangle(&signalBrush, x, Y, 1, 1);

	//		gf.DrawLine(&erasePen, 0, Y, WINDOW_WIDTH, Y);
	//	}
	//}
}