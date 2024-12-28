import React, { useState, useRef } from 'react';

const VariableAutoCompleteTextarea = ({ value, onChange, variableOptions }) => {
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

  return (
    <div style={{ position: 'relative' }}>
      {/* Textarea for typing */}
      <textarea
        ref={textareaRef}
        rows={3}
        style={{ width: '100%' }}
        value={value}
        onChange={handleInputChange}
        onClick={(e) => setCursorPosition(e.target.selectionStart)}
        onKeyDown={(e) => setCursorPosition(e.target.selectionStart)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)} // Delay to allow suggestion clicks
      />

      {/* Suggestions dropdown */}
      {showSuggestions && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            background: '#fff',
            border: '1px solid #ccc',
            width: '100%',
            zIndex: 999,
            maxHeight: '150px',
            overflowY: 'auto',
          }}
        >
          {filteredOptions.length > 0 ? (
            filteredOptions.map((option, index) => (
              <div
                key={index}
                style={{
                  padding: '0.5rem',
                  cursor: 'pointer',
                  borderBottom: '1px solid #eee',
                }}
                onMouseDown={() => handleSuggestionClick(option)}
              >
                {option}
              </div>
            ))
          ) : (
            <div style={{ padding: '0.5rem', color: '#999' }}>No suggestions</div>
          )}
        </div>
      )}
    </div>
  );
};

export default VariableAutoCompleteTextarea;