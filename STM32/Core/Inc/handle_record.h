#ifndef __HANDLE_RECORD_H
#define __HANDLE_RECORD_H

#include "stm32l4xx_hal.h"

// Human vocal freq ~ 70 ~ 1000Hz => 1ms to 14ms once, take 1500Hz. Sample Rate = 1500 * 2 = 3k as Min, take 20kHz // 40ms sample once
#define RECORD_T (0.05) //every ~ms handle record data once (current fft only support 2^n = 1024)
#define AUDIO_REC (1024 * 2) //Sample rate: approximately 48 * 25kHz

extern int32_t RecBuf[AUDIO_REC];
extern int32_t DataBuf[AUDIO_REC];
extern int32_t *ActualData;// Every data is AUDIO_REC / 2 large, may shift 0 or AUDIO_REC / 2

void StartRecord(DFSDM_Filter_HandleTypeDef *hdfsdm_filter);
__weak void Record_Callback();
void HAL_DFSDM_FilterRegConvCpltCallback(DFSDM_Filter_HandleTypeDef *hdfsdm_filter);
void HAL_DFSDM_FilterRegConvHalfCpltCallback(DFSDM_Filter_HandleTypeDef *hdfsdm_filter);

#endif
