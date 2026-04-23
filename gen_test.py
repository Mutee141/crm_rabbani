import pandas as pd
data = {
     'Employee ID': ['1700344', '1700213', '1700234', '1700044', '1700034'],
     'Date': ['2026-01-14', '2026-01-14', '2026-01-14', '2026-01-14', '2026-01-14'],
     'Check In': ['08:55:00', '09:15:00', '09:00:00', '09:00:00', '09:00:00'],
     'Check Out': ['18:05:00', '17:50:00', '18:10:00', '18:10:00', '18:10:00']
}
df = pd.DataFrame(data)
df.to_excel('attendance_test.xlsx', index=False)
print('File attendance_test.xlsx created!')
