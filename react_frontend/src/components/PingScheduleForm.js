// PingScheduleForm.js

import React, { useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import {
  Grid,
  TextField,
  Checkbox,
  FormControlLabel,
  Button,
  Typography,
  Paper,
  Box,
} from '@mui/material';

/**
 * PingScheduleForm
 * Handles the UI for "Every Day" vs. "Per Day" scheduling,
 * including multiple ping blocks per day.
 */
function PingScheduleForm() {
  // Access the parent form’s context
  const {
    register,
    watch,
    setValue,
    control,
  } = useFormContext();

  const scheduleMode = watch('scheduleMode');
  const studyLength = watch('studyLength');
  const perDaySchedule = watch('perDaySchedule');
  const everyDayPingsCount = watch('everyDayPingsCount');
  const everyDayPings = watch('everyDayPings');

  // Utility: create default ping block
  const getDefaultPingBlock = () => ({
    beginTime: '09:00',
    endTime: '17:00',
    nextDay: false,
  });

  // Handle dynamic array sizing for EVERY DAY pings
  useEffect(() => {
    if (scheduleMode !== 'everyDay') return;

    let newPings = [...everyDayPings];
    while (newPings.length < everyDayPingsCount) {
      newPings.push(getDefaultPingBlock());
    }
    if (newPings.length > everyDayPingsCount) {
      newPings = newPings.slice(0, everyDayPingsCount);
    }

    // Only update if the new value is different
    if (JSON.stringify(newPings) !== JSON.stringify(everyDayPings)) {
      setValue('everyDayPings', newPings);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [everyDayPingsCount, scheduleMode]);

  // Handle dynamic array sizing for PER DAY schedule
  useEffect(() => {
    if (scheduleMode !== 'perDay') return;

    const numericStudyLength = parseInt(studyLength, 10) || 0;
    const desiredLength = Math.max(1, numericStudyLength + 1);

    let updatedSchedule = [...perDaySchedule];
    while (updatedSchedule.length < desiredLength) {
      updatedSchedule.push({
        day: updatedSchedule.length,
        active: false,
        pings: [getDefaultPingBlock()],
      });
    }
    if (updatedSchedule.length > desiredLength) {
      updatedSchedule = updatedSchedule.slice(0, desiredLength);
    }

    updatedSchedule = updatedSchedule.map((dayObj) => {
      if (!dayObj.active) {
        return {
          ...dayObj,
          pings: [getDefaultPingBlock()],
        };
      }
      return dayObj;
    });

    // Only update if the new value is different
    if (JSON.stringify(updatedSchedule) !== JSON.stringify(perDaySchedule)) {
      setValue('perDaySchedule', updatedSchedule);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studyLength, scheduleMode]);

  // Switch between modes
  const handleSwitchMode = (mode) => {
    setValue('scheduleMode', mode);
  };

  // Add a new ping to a specific day
  const handleAddPingToDay = (dayIndex) => {
    const newSched = [...perDaySchedule];
    newSched[dayIndex].pings.push(getDefaultPingBlock());
    setValue('perDaySchedule', newSched);
  };

  // Remove a ping block from a day
  const handleRemovePingFromDay = (dayIndex, pingIndex) => {
    const newSched = [...perDaySchedule];
    newSched[dayIndex].pings.splice(pingIndex, 1);
    setValue('perDaySchedule', newSched);
  };

  // Clear a day’s pings
  const handleClearDay = (dayIndex) => {
    const newSched = [...perDaySchedule];
    newSched[dayIndex].pings = [getDefaultPingBlock()];
    newSched[dayIndex].active = false;
    setValue('perDaySchedule', newSched);
  };

  /**
   * RENDER
   */
  return (
    <Box sx={{ border: '1px solid #ccc', padding: 2, marginBottom: 2 }}>
      <Typography variant="h6">Schedule</Typography>

      {/* Schedule Mode Selection */}
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={scheduleMode === 'everyDay'}
                onChange={() => handleSwitchMode('everyDay')}
              />
            }
            label="Every Day"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={scheduleMode === 'perDay'}
                onChange={() => handleSwitchMode('perDay')}
              />
            }
            label="Per Day"
          />
        </Grid>
      </Grid>

      {/* Every Day Mode */}
      {scheduleMode === 'everyDay' && (
        <Box sx={{ padding: 2, border: '1px solid #ddd', marginTop: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="Number of pings per day"
                type="number"
                inputProps={{ min: 1 }}
                {...register('everyDayPingsCount', { min: 1 })}
                fullWidth
              />
            </Grid>

            {everyDayPings.map((ping, i) => (
              <React.Fragment key={i}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label={`Ping ${i + 1} - Begin Time`}
                    type="time"
                    value={ping.beginTime}
                    onChange={(e) => {
                      const arr = [...everyDayPings];
                      arr[i].beginTime = e.target.value;
                      setValue('everyDayPings', arr);
                    }}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label={`Ping ${i + 1} - End Time`}
                    type="time"
                    value={ping.endTime}
                    onChange={(e) => {
                      const arr = [...everyDayPings];
                      arr[i].endTime = e.target.value;
                      setValue('everyDayPings', arr);
                    }}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={ping.nextDay}
                        onChange={(e) => {
                          const arr = [...everyDayPings];
                          arr[i].nextDay = e.target.checked;
                          setValue('everyDayPings', arr);
                        }}
                      />
                    }
                    label="Next Day?"
                  />
                </Grid>
              </React.Fragment>
            ))}
          </Grid>
        </Box>
      )}

      {/* Per Day Mode */}
      {scheduleMode === 'perDay' && (
        <Box sx={{ padding: 2, border: '1px solid #ddd', marginTop: 2 }}>
          {perDaySchedule.map((dayObj, idx) => (
            <Paper key={idx} sx={{ padding: 2, marginBottom: 2 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={dayObj.active}
                    onChange={(e) => {
                      const newSched = [...perDaySchedule];
                      newSched[idx].active = e.target.checked;
                      setValue('perDaySchedule', newSched);
                    }}
                  />
                }
                label={
                  `Day ${dayObj.day}` +
                  (dayObj.day === 0 ? ' (Day of participant signup)' : '')
                }
              />

              {dayObj.active && (
                <>
                  {dayObj.pings.map((ping, pingIndex) => (
                    <Paper key={pingIndex} sx={{ padding: 2, marginBottom: 2 }}>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item xs={12} sm={3}>
                          <TextField
                            label="Start Time"
                            type="time"
                            value={ping.beginTime}
                            onChange={(e) => {
                              const newSched = [...perDaySchedule];
                              newSched[idx].pings[pingIndex].beginTime = e.target.value;
                              setValue('perDaySchedule', newSched);
                            }}
                            fullWidth
                          />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <TextField
                            label="End Time"
                            type="time"
                            value={ping.endTime}
                            onChange={(e) => {
                              const newSched = [...perDaySchedule];
                              newSched[idx].pings[pingIndex].endTime = e.target.value;
                              setValue('perDaySchedule', newSched);
                            }}
                            fullWidth
                          />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={ping.nextDay}
                                onChange={(e) => {
                                  const newSched = [...perDaySchedule];
                                  newSched[idx].pings[pingIndex].nextDay =
                                    e.target.checked;
                                  setValue('perDaySchedule', newSched);
                                }}
                              />
                            }
                            label="Next Day?"
                          />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                          <Button
                            variant="outlined"
                            color="secondary"
                            onClick={() => handleRemovePingFromDay(idx, pingIndex)}
                            fullWidth
                          >
                            Remove Ping
                          </Button>
                        </Grid>
                      </Grid>
                    </Paper>
                  ))}

                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleAddPingToDay(idx)}
                    sx={{ marginTop: 1 }}
                  >
                    + Add Another Ping
                  </Button>

                  <Button
                    variant="outlined"
                    color="secondary"
                    onClick={() => handleClearDay(idx)}
                    sx={{ marginLeft: 1, marginTop: 1 }}
                  >
                    Clear This Day
                  </Button>
                </>
              )}
            </Paper>
          ))}
        </Box>
      )}
    </Box>
  );
}

export default PingScheduleForm;