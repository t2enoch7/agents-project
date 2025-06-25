import React from "react";
import { Box, Typography, Paper } from "@mui/material";

const ProfilePage: React.FC = () => {
  return (
    <Box>
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          This is a placeholder for the patient profile page. You can add
          profile editing features here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ProfilePage;
