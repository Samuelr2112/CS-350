# CS-350

# Thermostat and PWM LED Control Projects

These two projects reflect my progress and growing skills in emerging systems architectures and technologies. Through these assignments, I explored how to interface hardware components with software, analyzed hardware performance factors, and applied industry best practices to make the systems maintainable and adaptable.

---

## Project 1: Thermostat Prototype

The first project was a smart thermostat prototype designed for SysTec. I used a Raspberry Pi, a temperature sensor, LEDs, buttons, and an LCD display to create a system that can manage heating, cooling, and off states. The thermostat reads room temperature and adjusts the LEDs and display accordingly. I also implemented serial communication via UART to send regular status updates.

One part of the project I’m particularly proud of is how well the state machine worked. I designed it to be simple yet effective, allowing smooth transitions between heating, cooling, and off modes. It also felt rewarding to see the components like LEDs and buttons interact as expected. However, I see room for improvement in optimizing the UART communication for faster updates and possibly integrating a Wi-Fi connection in the future.

This project taught me a lot about Python object-oriented programming and hardware integration. These skills will definitely come in handy in future projects where I need to manage stateful hardware components. Plus, I learned more about debugging hardware issues, which is invaluable when working with embedded systems.

---

## Project 2: PWM LED Control

The second project was simpler but equally important. I worked on controlling an LED's brightness using Pulse Width Modulation (PWM). The goal was to make the LED smoothly fade in and out. This involved configuring GPIO pins on the Raspberry Pi, adjusting the PWM duty cycle, and handling exceptions to ensure clean exits from the program.

I’m happy with how smoothly the LED fading effect turned out. It required fine-tuning the duty cycle and sleep intervals to make the transitions visually appealing. That said, I faced some challenges with indentation errors due to mixing tabs and spaces, but fixing those improved my attention to detail in coding.

This project enhanced my understanding of PWM and GPIO control. These concepts are transferable to other components, such as motors or even more complex circuits. I also feel more confident handling low-level hardware programming, which is critical for projects involving embedded systems.

---

## Reflecting on My Journey

Throughout these projects, I’ve expanded my support network by learning from online documentation, Raspberry Pi forums, and examples from previous course modules. I’ve also learned to be more methodical in troubleshooting hardware-software interactions, which has reduced the time I spend on debugging.

To make my code more maintainable and adaptable, I focused on clear comments, proper variable naming, and keeping functions focused on single responsibilities. These best practices have made the projects easier to revisit, both for me and others who may work with my code in the future.

---

## How to Run the Code
- Clone the repository: `git clone <your-repo-url>`
- For `thermostat.py`, ensure you have the required hardware (Raspberry Pi, temperature sensor, LEDs, buttons).
- For `Milestone1.py`, set up a Raspberry Pi with GPIO pin 18 connected to an LED.
