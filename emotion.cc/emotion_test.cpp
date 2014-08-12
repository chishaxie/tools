#include "emotion_code.h"

#include <iostream>

using namespace std;

#define HEX_TO_BYTE(c) ((c) >= 'a' && (c) <= 'f'? ((c) - 'a' + 10): ((c) - '0'))

static string Hex2Buf(const char *szHex)
{
	string sRet;
	for (size_t i = 0; szHex[i] != '\0' && szHex[i+1] != '\0'; i += 2)
		sRet += static_cast<char>((HEX_TO_BYTE(szHex[i]) << 4) + HEX_TO_BYTE(szHex[i+1]));
	return sRet;
}

int main(int argc, char *argv[])
{
	string sInput = Hex2Buf("ee9096202fe88cb6e58fb6e89b8b"); // /z发怒 /茶叶蛋
	string sOutput;
	ReplaceEmotionCode(sOutput, sInput);
	cout << sOutput << endl;
	return 0;
}
