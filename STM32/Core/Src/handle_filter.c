#include <inttypes.h>
#include <stdio.h>
#include "handle_filter.h"

//float s_arrFFTInput[AUDIO_REC / 2] = {0};      //FFT 输入缓冲区
//float s_arrFFTMid[AUDIO_REC / 2] = {0};
//float s_arrFFTOutput[AUDIO_REC / 2] = {0};     //FFT 输出缓冲区
//float *s_arrFFTMag = s_arrFFTInput;
//float *s_arrFFTResult = s_arrFFTOutput;
//arm_rfft_fast_instance_f32 s_structRfft;        //FFT 控制结构体
//float THRESHOLD = 30000.0;

float s_arrFFTInput[AUDIO_REC / 2] = {0};      //FFT 输入缓冲区
float s_arrFFTMid[AUDIO_REC / 2] = {0};
float s_arrFFTOutput[AUDIO_REC / 2] = {0};     //FFT 输出缓冲区
float *s_arrFFTMag = s_arrFFTInput;
float *s_arrFFTResult = s_arrFFTOutput;
arm_rfft_fast_instance_f32 s_structRfft;        //FFT 控制结构体
float THRESHOLD = 200000.0;
void init_filter() {
	arm_rfft_1024_fast_init_f32(&s_structRfft);
}

int16_t handle_filter(int32_t* Actual_Data) {
	int16_t assessed_freq;
	for (int i = 0; i < AUDIO_REC / 2; i++) {
		s_arrFFTInput[i] = (float)ActualData[i];
	}
	arm_rfft_fast_f32(&s_structRfft, s_arrFFTInput, s_arrFFTOutput, 0);
	arm_cmplx_mag_f32(s_arrFFTOutput, s_arrFFTInput, 512);      //求解模值
	for(int i = 511; i >= 0; i--) {
		s_arrFFTInput[2 * i + 1] = 0.0;
		s_arrFFTInput[2 * i] = s_arrFFTInput[i];
	}
	arm_rfft_fast_f32(&s_structRfft, s_arrFFTInput, s_arrFFTOutput, 1);
	int f = 1;
	float max = 0;
	for (int i = 60; i < 1000; i++) {
		if (s_arrFFTOutput[i] > max && 1000 / RECORD_T / i >= 65 && 1000 / RECORD_T / i <= 440) {
			f = i;
			max = s_arrFFTOutput[i];
		}
	}
	if (max <= THRESHOLD) {
		if (1000 / RECORD_T / f <= 130 && max > (THRESHOLD * 0.75)) {
			assessed_freq = 1000 / RECORD_T / f;
		} else {
			assessed_freq = 0;
		}
	} else {
		assessed_freq = 1000 / RECORD_T / f;
	}
	int intmax = max;
	printf("%d|%d|%d\n", assessed_freq, intmax, assessed_freq < 0 ? 10000 : 0);
	return assessed_freq;
}

//int16_t handle_filter(int32_t* Actual_Data) {
//	int16_t assessed_freq;
//	int32_t cur_amp, max_amp = -300000;
//	for (int i = 0; i < AUDIO_REC / 2; i++) {
//		s_arrFFTInput[i] = ActualData[i];
//	}
//	for (int i = 0; i < 49; i++) {
//		cur_amp = autocorrelation(s_arrFFTInput, shift[i]);
//		if (cur_amp > max_amp) {
//			max_amp = cur_amp;
//			assessed_freq = pitch[i];
//		}
//	}
//	if (max_amp <= THRESHOLD) {
//		assessed_freq = -1000 / RECORD_T / assessed_freq;
//	} else {
//		assessed_freq = 1000 / RECORD_T / assessed_freq;
//	}
//	return assessed_freq;
//}

float autocorrelation(float* arr, uint16_t shift) {
	float sum = 0;
	arm_mult_f32(s_arrFFTInput, s_arrFFTInput + shift, s_arrFFTMid + shift, 1024 - shift);
	arm_mult_f32(s_arrFFTInput + 1024 - shift, s_arrFFTInput, s_arrFFTMid, shift);
	for (int i = 0; i < 256; i++) {
		sum += s_arrFFTMid[4 * i];
		sum += s_arrFFTMid[4 * i + 1];
		sum += s_arrFFTMid[4 * i + 2];
		sum += s_arrFFTMid[4 * i + 3];
	}
	return sum;
}

//q31_t autocorrelation(q31_t* arr, uint16_t shift) {
//	int32_t sum = 0;
//	arm_mult_q31(s_arrFFTInput, s_arrFFTInput + shift, s_arrFFTMid + shift, (AUDIO_REC / 2) - shift);
//	arm_mult_q31(s_arrFFTInput + (AUDIO_REC / 2) - shift, s_arrFFTInput, s_arrFFTMid, shift);
//	for (int i = 0; i < 256; i++) {
//		sum += (s_arrFFTMid[4 * i] >> 10);
//		sum += (s_arrFFTMid[4 * i + 1] >> 10);
//		sum += (s_arrFFTMid[4 * i + 2] >> 10);
//		sum += (s_arrFFTMid[4 * i + 3] >> 10);
//	}
//	return sum;
//}

int freq_comp(const void* a, const void* b) {
	FreqData* freq_a = (FreqData*) a;
	FreqData* freq_b = (FreqData*) b;
	if (freq_a->freq == freq_b->freq) {
		return freq_a->freq - freq_b->freq;
	} else {
		return freq_a->time - freq_b->time;
	}
}

FreqData freq_heuristic(FreqData* acc_data) {
	uint32_t last_time;
	//float TONE = 1.0595;
	FreqData assessed_answer;
	last_time = acc_data[2].time;
	qsort(acc_data, 3, sizeof(FreqData), freq_comp);
	assessed_answer.freq = acc_data[1].freq;
	assessed_answer.time = last_time;
	return assessed_answer;
}
