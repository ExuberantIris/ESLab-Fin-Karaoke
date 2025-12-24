#include "handle_record.h"
#include <stdio.h>
#include <inttypes.h>
int32_t RecBuf[AUDIO_REC];
int32_t DataBuf[AUDIO_REC];
int32_t *ActualData;// Every data is AUDIO_REC / 2 large, may shift 0 or AUDIO_REC / 2
int32_t runned[1] = {0};
void StartRecord(DFSDM_Filter_HandleTypeDef *hdfsdm_filter)
{
	HAL_DFSDM_FilterRegularStart_DMA(hdfsdm_filter, RecBuf, AUDIO_REC);
}

void HAL_DFSDM_FilterRegConvCpltCallback(DFSDM_Filter_HandleTypeDef *hdfsdm_filter)
{
	for (int i = AUDIO_REC / 2; i < AUDIO_REC; i++) {
		DataBuf[i] = (RecBuf[i] >> 8) << 8;
	}
	ActualData = DataBuf + AUDIO_REC / 2;
	Record_Callback();
}

/**
  * @brief  Half regular conversion complete callback.
  * @param  hdfsdm_filter DFSDM filter handle.
  * @retval None
  */
void HAL_DFSDM_FilterRegConvHalfCpltCallback(DFSDM_Filter_HandleTypeDef *hdfsdm_filter)
{
	for (int i = 0; i < AUDIO_REC / 2; i++) {
		DataBuf[i] = (RecBuf[i] >> 8) << 8;
	}
	ActualData = DataBuf;
	Record_Callback();
}
