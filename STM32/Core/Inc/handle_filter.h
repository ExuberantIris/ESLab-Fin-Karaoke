#ifndef __HANDLE_FILTER_H
#define __HANDLE_FILTER_H

#include <stdlib.h>
#include <math.h>
#include "stm32l4xx_hal.h"
#include "arm_math.h"
#include "handle_record.h"
#include "pitch_data.h"

typedef struct {
	int16_t freq;
	uint32_t time;
} FreqData;

void init_filter();
int16_t handle_filter(int32_t* Actual_Data);
float autocorrelation(float* arr, uint16_t shift);
int freq_comp(const void* a, const void* b);
FreqData freq_heuristic(FreqData* acc_data);

#endif
