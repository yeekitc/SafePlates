import {
    Box,
    Typography,
    TextField,
    Button,
    Paper,
    Container
} from '@mui/material';

function AddReview() {
    return (
        <Container maxWidth="md">
            <Box sx={{ py: 4 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                    <Typography variant="h3" component="h1" sx={{ mr: 2 }}>
                        Cali Pizza
                    </Typography>
                </Box>

                {/* Form */}
                <Paper sx={{ p: 4 }}>
                    <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {/* Dish Name */}
                        <TextField
                            fullWidth
                            label="Dish"
                            placeholder="Input a dish!"
                            variant="outlined"
                        />

                        {/* Image Upload */}
                        <TextField
                            fullWidth
                            type="file"
                            label="Image of the Dish"
                            InputLabelProps={{ shrink: true }}
                            variant="outlined"
                        />

                        {/* Dietary Restrictions */}
                        <TextField
                            fullWidth
                            label="NOT Friendly to..."
                            placeholder="All the dietary restrictions that this dish works with!"
                            variant="outlined"
                            multiline
                            rows={2}
                        />

                        {/* Comments */}
                        <TextField
                            fullWidth
                            label="Comments"
                            placeholder="How was your experience? Let us know!"
                            variant="outlined"
                            multiline
                            rows={4}
                        />
                    </Box>
                </Paper>
            </Box>
            <Button variant="contained" sx={{
                backgroundColor: '#F3B829',
                color: 'black', 
            }}>Add Review</Button>
        </Container>
    );
}

export default AddReview;