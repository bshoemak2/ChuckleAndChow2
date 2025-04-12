import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  scrollContainer: { 
    flex: 1, 
    backgroundColor: '#FFFACD' // Lemon Chiffon
  },
  scrollContent: { 
    paddingBottom: 20 
  },
  container: { 
    padding: 15 
  },
  header: { 
    fontSize: 32, 
    fontWeight: 'bold', 
    color: '#FF4500', // Orange Red
    textAlign: 'center', 
    marginVertical: 10, 
    textShadowColor: '#FFD700', // Yellow shadow
    textShadowOffset: { width: 2, height: 2 }, 
    textShadowRadius: 5 
  },
  subheader: { 
    fontSize: 18, 
    color: '#FF00A0', // Hot Pink
    textAlign: 'center', 
    marginBottom: 10, 
    fontStyle: 'italic' 
  },
  trustSection: { 
    flexDirection: 'row', 
    justifyContent: 'space-around', 
    marginVertical: 10 
  },
  trustText: { 
    fontSize: 14, 
    color: '#32CD32', // Lime Green
    fontWeight: 'bold' 
  },
  inputSection: { 
    marginVertical: 15, 
    backgroundColor: '#F0E68C', // Khaki
    padding: 10, 
    borderRadius: 10, 
    borderWidth: 2, 
    borderColor: '#FF69B4' // Hot Pink
  },
  inputLabel: { 
    fontSize: 18, 
    fontWeight: 'bold', 
    textAlign: 'center', 
    padding: 5, 
    borderRadius: 5, 
    marginBottom: 5 
  },
  picker: { 
    height: 50, 
    width: '100%', 
    borderWidth: 2, 
    borderRadius: 10, 
    marginBottom: 10 
  },
  spinnerContainer: { 
    alignItems: 'center', 
    marginVertical: 20 
  },
  spinnerText: { 
    fontSize: 16 
  },
  buttonRow: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    justifyContent: 'space-around', 
    marginVertical: 10 
  },
  errorContainer: { 
    alignItems: 'center', 
    marginVertical: 10 
  },
  error: { 
    fontSize: 16 
  },
  recipeCard: { 
    backgroundColor: '#FFF8DC', // Cornsilk for a rustic feel
    padding: 20, // More space
    borderRadius: 15, 
    marginVertical: 10, 
    borderWidth: 3, 
    borderColor: '#FF4500', // Orange Red
    shadowColor: '#FF69B4', // Hot Pink shadow
    shadowOffset: { width: 0, height: 4 }, 
    shadowOpacity: 0.6, // Bolder shadow
    shadowRadius: 6, // Smoother spread
    elevation: 8 // Deeper Android depth
  },
  recipeTitle: { 
    fontSize: 24, 
    fontWeight: 'bold', 
    color: '#FF00A0', // Hot Pink
    textAlign: 'center', 
    marginBottom: 10, 
    textShadowColor: '#FFD700', // Yellow shadow
    textShadowOffset: { width: 1, height: 1 }, 
    textShadowRadius: 3 
  },
  recipeSectionContainer: { 
    marginVertical: 8, 
    padding: 10, 
    backgroundColor: '#F0FFF0', // Honeydew
    borderRadius: 10, 
    borderWidth: 2, 
    borderColor: '#32CD32' // Lime Green
  },
  recipeSection: { 
    fontSize: 18, 
    fontWeight: 'bold', 
    color: '#FF4500', // Orange Red
    marginBottom: 5 
  },
  recipeContent: { 
    fontSize: 14, 
    color: '#333', 
    marginLeft: 5 
  },
  recipeItem: { 
    fontSize: 14, 
    color: '#4ECDC4', // Turquoise
    marginLeft: 10, 
    marginTop: 3 
  },
  recipeActions: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    justifyContent: 'space-around', 
    marginTop: 10 
  },
  copyButton: { 
    backgroundColor: '#FF69B4', // Hot Pink
    padding: 10, 
    borderRadius: 5, 
    marginVertical: 5, 
    borderWidth: 2, 
    borderColor: '#FFD700' // Yellow
  },
  copyButtonText: { 
    color: '#FFF', 
    textAlign: 'center', 
    fontWeight: 'bold' 
  },
  favoriteItem: { 
    fontSize: 16, 
    color: '#FFD93D', // Gold
    padding: 10, 
    borderBottomWidth: 1, 
    borderBottomColor: '#ccc' 
  },
  affiliateSection: { 
    marginVertical: 20, 
    padding: 15, 
    backgroundColor: '#FF1493', // Deep Pink
    borderRadius: 15, 
    borderWidth: 3, 
    borderColor: '#FFD700', // Yellow
    alignItems: 'center' 
  },
  affiliateHeader: { 
    fontSize: 24, 
    fontWeight: 'bold', 
    color: '#FFD700', // Yellow
    textAlign: 'center', 
    marginBottom: 10, 
    textShadowColor: '#FF4500', // Orange Red shadow
    textShadowOffset: { width: 2, height: 2 }, 
    textShadowRadius: 5 
  },
  affiliateButton: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: '#32CD32', // Lime Green
    padding: 10, 
    borderRadius: 10, 
    marginVertical: 5, 
    borderWidth: 2, 
    borderColor: '#FF00A0', // Hot Pink
    width: '100%' 
  },
  affiliateImage: { 
    width: 60, 
    height: 60, 
    marginRight: 10, 
    borderRadius: 5, 
    borderWidth: 2, 
    borderColor: '#FFD700' // Yellow
  },
  affiliateText: { 
    fontSize: 16, 
    color: '#FFF', 
    fontWeight: 'bold', 
    flexShrink: 1 
  },
  affiliateDisclaimer: { 
    fontSize: 12, 
    color: '#FFFF00', // Bright Yellow
    textAlign: 'center', 
    marginTop: 10 
  },
  footer: { 
    alignItems: 'center', 
    padding: 20, 
    marginTop: 20, 
    backgroundColor: '#FFD700', // Gold
    borderTopWidth: 3, 
    borderTopColor: '#FF4500', // Orange Red
  },
  footerLogo: {
    width: 80,
    height: 80,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#FF00A0',
  },
  footerCopyright: {
    fontSize: 14,
    color: '#FF4500',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  footerLinks: {
    alignItems: 'center',
    marginBottom: 10,
  },
  footerPrivacyLink: {
    marginBottom: 8,
  },
  footerPrivacyText: {
    fontSize: 16,
    color: '#FF00A0',
    textDecorationLine: 'underline',
    fontWeight: 'bold',
  },
  footerContactText: {
    fontSize: 12,
    color: '#FFF',
    textAlign: 'center',
  },
  footerEmailLink: {
    color: '#FF00A0',
    textDecorationLine: 'underline',
  },
  footerFallback: {
    width: 80,
    height: 80,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)', // Semi-transparent black
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFF8DC', // Cornsilk to match recipe card
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    borderWidth: 3,
    borderColor: '#FF4500', // Orange Red
    shadowColor: '#FF69B4', // Hot Pink shadow
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.6,
    shadowRadius: 6,
    elevation: 8,
    width: '80%',
    maxWidth: 400,
  },
  modalImage: {
    width: 100,
    height: 100,
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#FFD700', // Yellow
    borderRadius: 10,
  },
  modalText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF00A0', // Hot Pink
    textAlign: 'center',
    marginBottom: 10,
  },
  modalSubText: {
    fontSize: 16,
    color: '#4ECDC4', // Turquoise
    textAlign: 'center',
    marginBottom: 20,
  },
  modalButton: {
    backgroundColor: '#FF9900', // Orange for consistency with cart button
    padding: 10,
    borderRadius: 5,
    borderWidth: 2,
    borderColor: '#FFD700', // Yellow
    width: '50%',
    alignItems: 'center',
  },
  modalButtonText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  favorites: {
    marginVertical: 10,
    padding: 10,
    backgroundColor: '#FFF8DC', // Cornsilk
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#FF4500', // Orange Red
  },
  subtitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FF00A0', // Hot Pink
    marginBottom: 10,
    textAlign: 'center',
  },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  input: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
    marginRight: 10,
  },
  favItemContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 5,
  },
  favItem: {
    fontSize: 16,
    color: '#FFD93D', // Gold
    padding: 10,
  },
  noFavorites: {
    fontSize: 16,
    color: '#FF4500', // Orange Red
    textAlign: 'center',
    marginTop: 10,
  },
});