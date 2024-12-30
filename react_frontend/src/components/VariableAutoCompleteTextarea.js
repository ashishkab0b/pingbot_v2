// VariableAutoCompleteTextarea.js
import React, { useState, useRef } from 'react';
import { TextField, Paper, List, ListItem, ListItemText } from '@mui/material';

const VariableAutoCompleteTextarea = ({
  value,
  onChange,
  variableOptions,
  label,
  error,
  helperText,
  variant = 'outlined',
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredOptions, setFilteredOptions] = useState([]);
  const [cursorPosition, setCursorPosition] = useState(null);
  const textareaRef = useRef(null);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    const cursorPos = e.target.selectionStart;
    setCursorPosition(cursorPos);

    // Detect if "<" is typed to trigger suggestions
    const match = inputValue.slice(0, cursorPos).match(/<(\w*)$/);
    if (match) {
      const searchTerm = match[1].toUpperCase();
      const filtered = variableOptions.filter((option) =>
        option.startsWith(`<${searchTerm}`)
      );
      setFilteredOptions(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }

    onChange(inputValue);
  };

  const handleSuggestionClick = (suggestion) => {
    if (textareaRef.current) {
      const inputValue = value;
      const beforeCursor = inputValue.slice(0, cursorPosition);
      const afterCursor = inputValue.slice(cursorPosition);

      // Replace the current "<" and any following text with the selected suggestion
      const updatedValue = beforeCursor.replace(/<\w*$/, suggestion) + afterCursor;

      onChange(updatedValue);
      setShowSuggestions(false);

      // Move the cursor to the end of the inserted suggestion
      const newCursorPos = beforeCursor.replace(/<\w*$/, suggestion).length;
      setCursorPosition(newCursorPos);
      setTimeout(() => textareaRef.current.setSelectionRange(newCursorPos, newCursorPos), 0);
    }
  };

  const handleBlur = () => {
    // Delay hiding suggestions to allow click event to register
    setTimeout(() => setShowSuggestions(false), 100);
  };

  return (
    <div style={{ position: 'relative' }}>
      <TextField
        label={label}
        multiline
        minRows={3}
        variant={variant}
        fullWidth
        inputRef={textareaRef}
        value={value}
        onChange={handleInputChange}
        onClick={(e) => setCursorPosition(e.target.selectionStart)}
        onKeyDown={(e) => setCursorPosition(e.target.selectionStart)}
        onBlur={handleBlur}
        error={error}
        helperText={helperText}
      />

      {/* Suggestions dropdown */}
      {showSuggestions && (
        <Paper
          style={{
            position: 'absolute',
            top: textareaRef.current?.offsetHeight || 0,
            left: 0,
            right: 0,
            zIndex: 999,
            maxHeight: '150px',
            overflowY: 'auto',
          }}
        >
          <List dense>
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option, index) => (
                <ListItem
                  button
                  key={index}
                  onMouseDown={() => handleSuggestionClick(option)}
                >
                  <ListItemText primary={option} />
                </ListItem>
              ))
            ) : (
              <ListItem>
                <ListItemText primary="No suggestions" />
              </ListItem>
            )}
          </List>
        </Paper>
      )}
    </div>
  );
};

export default VariableAutoCompleteTextarea;