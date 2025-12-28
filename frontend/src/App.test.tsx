/*import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
*/

import React from "react";
import { render, screen } from "@testing-library/react";
//import MessageBubble from "./MessageBubble";

test("renders user message bubble", () => {
  render(<MessageBubble sender="user" text="Hello" />);
  expect(screen.getByText("Hello")).toHaveClass("bg-blue-500");
});
