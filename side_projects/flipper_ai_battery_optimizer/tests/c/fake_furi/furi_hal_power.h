#ifndef BATTERY_TEST_FAKE_FURI_HAL_POWER_H
#define BATTERY_TEST_FAKE_FURI_HAL_POWER_H

#include <stdbool.h>
#include <stdint.h>

/* Host-side mock signatures for exactly the three current project API calls.
 * These mocks are NOT the real Momentum/Flipper SDK.
 */
uint8_t furi_hal_power_get_pct(void);
uint8_t furi_hal_power_get_bat_health_pct(void);
bool furi_hal_power_is_charging(void);
#endif
