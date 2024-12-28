import React, { useEffect } from 'react';
import { useFormContext } from 'react-hook-form';

/**
 * PingScheduleForm
 * Handles the UI for "every day" vs. "per day" scheduling,
 * including multiple ping blocks per day.
 */
function PingScheduleForm() {
  // Access the parent form’s context
  const {
    register,
    watch,
    setValue,
    // You might also need getValues or other methods from useFormContext
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
    nextDay: false
  });

  // Utility: create default day object
  const getDefaultDayObj = (dayIndex) => ({
    day: dayIndex,
    active: false,
    pings: [getDefaultPingBlock()]
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
  }, [everyDayPingsCount, everyDayPings, scheduleMode, setValue]);

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
        pings: [{ beginTime: '09:00', endTime: '17:00', nextDay: false }]
      });
    }
    if (updatedSchedule.length > desiredLength) {
      updatedSchedule = updatedSchedule.slice(0, desiredLength);
    }
  
    updatedSchedule = updatedSchedule.map((dayObj, index) => {
      if (!dayObj.active) {
        return {
          ...dayObj,
          pings: [{ beginTime: '09:00', endTime: '17:00', nextDay: false }]
        };
      }
      return dayObj;
    });
  
    // Only update if the new value is different
    if (JSON.stringify(updatedSchedule) !== JSON.stringify(perDaySchedule)) {
      setValue('perDaySchedule', updatedSchedule);
    }
  }, [studyLength, scheduleMode, perDaySchedule, setValue]);

  // Switch from everyDay to perDay
  const handleSwitchToPerDay = () => {
    // Optional: copy just day 0 or do some minimal logic
    // Or do nothing except set scheduleMode
    setValue('scheduleMode', 'perDay');
  };

  // Switch from perDay back to everyDay, auto-populate from day 0
  const handleSwitchToEveryDay = () => {
    const day0 = perDaySchedule[0];
    if (day0 && day0.active) {
      if (day0.pings.length !== everyDayPingsCount) {
        setValue('everyDayPingsCount', day0.pings.length);
      }
      if (JSON.stringify(day0.pings) !== JSON.stringify(everyDayPings)) {
        setValue(
          'everyDayPings',
          day0.pings.map((p) => ({ ...p }))
        );
      }
    }
    setValue('scheduleMode', 'everyDay');
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

  // Clear a day’s pings (instead of removing the day entirely)
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
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
      <p>
        <strong>Schedule Mode:</strong> {scheduleMode}
      </p>

      {/* =============== EVERY DAY MODE =============== */}
      {scheduleMode === 'everyDay' && (
        <div style={{ padding: '1rem', border: '1px solid #ddd' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label>Number of pings per day:</label>
            <input
              type="number"
              style={{ width: '60px', marginLeft: '0.5rem' }}
              {...register('everyDayPingsCount', { min: 1 })}
            />
          </div>

          {everyDayPings.map((ping, i) => (
            <div
              key={i}
              style={{ border: '1px solid #eee', padding: '0.5rem', marginBottom: '0.5rem' }}
            >
              <div style={{ marginBottom: '0.5rem' }}>
                <label>Begin Time</label>
                <input
                  type="time"
                  style={{ marginLeft: '0.5rem' }}
                  value={ping.beginTime}
                  onChange={(e) => {
                    const arr = [...everyDayPings];
                    arr[i].beginTime = e.target.value;
                    setValue('everyDayPings', arr);
                  }}
                />
              </div>
              <div>
                <label>End Time</label>
                <input
                  type="time"
                  style={{ marginLeft: '0.5rem' }}
                  value={ping.endTime}
                  onChange={(e) => {
                    const arr = [...everyDayPings];
                    arr[i].endTime = e.target.value;
                    setValue('everyDayPings', arr);
                  }}
                />
                <label style={{ marginLeft: '0.5rem' }}>
                  <input
                    type="checkbox"
                    checked={ping.nextDay}
                    onChange={(e) => {
                      const arr = [...everyDayPings];
                      arr[i].nextDay = e.target.checked;
                      setValue('everyDayPings', arr);
                    }}
                  />
                  Next Day?
                </label>
              </div>
            </div>
          ))}

          <button type="button" onClick={handleSwitchToPerDay}>
            Switch to Per Day
          </button>
        </div>
      )}

      {/* =============== PER DAY MODE =============== */}
      {scheduleMode === 'perDay' && (
        <div style={{ padding: '1rem', border: '1px solid #ddd' }}>
          <button type="button" onClick={handleSwitchToEveryDay}>
            Switch to Every Day
          </button>

          {perDaySchedule.map((dayObj, idx) => (
            <div
              key={idx}
              style={{
                border: '1px solid #eee',
                padding: '0.5rem',
                marginTop: '1rem'
              }}
            >
              <label>
                <input
                  type="checkbox"
                  checked={dayObj.active}
                  onChange={(e) => {
                    const newSched = [...perDaySchedule];
                    newSched[idx].active = e.target.checked;
                    setValue('perDaySchedule', newSched);
                  }}
                />
                Day {dayObj.day}
                {dayObj.day === 0 && ' (Day of participant signup)'}
              </label>

              {dayObj.active && (
                <>
                  {dayObj.pings.map((ping, pingIndex) => (
                    <div
                      key={pingIndex}
                      style={{
                        border: '1px solid #ddd',
                        padding: '0.5rem',
                        margin: '0.5rem 0'
                      }}
                    >
                      <div style={{ marginBottom: '0.5rem' }}>
                        <label>Start Time</label>
                        <input
                          type="time"
                          style={{ marginLeft: '0.5rem' }}
                          value={ping.beginTime}
                          onChange={(e) => {
                            const newSched = [...perDaySchedule];
                            newSched[idx].pings[pingIndex].beginTime =
                              e.target.value;
                            setValue('perDaySchedule', newSched);
                          }}
                        />
                      </div>

                      <div>
                        <label>End Time</label>
                        <input
                          type="time"
                          style={{ marginLeft: '0.5rem' }}
                          value={ping.endTime}
                          onChange={(e) => {
                            const newSched = [...perDaySchedule];
                            newSched[idx].pings[pingIndex].endTime =
                              e.target.value;
                            setValue('perDaySchedule', newSched);
                          }}
                        />
                        <label style={{ marginLeft: '0.5rem' }}>
                          <input
                            type="checkbox"
                            checked={ping.nextDay}
                            onChange={(e) => {
                              const newSched = [...perDaySchedule];
                              newSched[idx].pings[pingIndex].nextDay =
                                e.target.checked;
                              setValue('perDaySchedule', newSched);
                            }}
                          />
                          Next Day?
                        </label>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleRemovePingFromDay(idx, pingIndex)}
                        style={{ marginTop: '0.5rem' }}
                      >
                        Remove Ping
                      </button>
                    </div>
                  ))}

                  <button
                    type="button"
                    onClick={() => handleAddPingToDay(idx)}
                  >
                    + Add Another Ping
                  </button>
                  <br />
                  <button
                    type="button"
                    onClick={() => handleClearDay(idx)}
                    style={{ marginTop: '0.5rem' }}
                  >
                    Clear This Day
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PingScheduleForm;