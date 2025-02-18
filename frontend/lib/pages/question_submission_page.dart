import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class QuestionSubmissionPage extends StatefulWidget {
  @override
  _QuestionSubmissionPageState createState() => _QuestionSubmissionPageState();
}

class _QuestionSubmissionPageState extends State<QuestionSubmissionPage> {
  final _formKey = GlobalKey<FormState>();
  String title = '';
  String body = '';
  String category = 'general';

  void _submit() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      final apiService = Provider.of<APIService>(context, listen: false);
      try {
        final cleanCategory = category.trim().toLowerCase();
        await apiService.createQuestion(title, body, cleanCategory);
        Navigator.pop(context, true);
      } catch (e) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error submitting question')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Submit Question')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                decoration: InputDecoration(labelText: 'Title'),
                onSaved: (value) => title = value ?? '',
                validator: (value) => (value == null || value.isEmpty)
                    ? 'Please enter a title'
                    : null,
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Body'),
                onSaved: (value) => body = value ?? '',
                validator: (value) => (value == null || value.isEmpty)
                    ? 'Please enter the body'
                    : null,
              ),
              TextFormField(
                initialValue: category,
                decoration: InputDecoration(labelText: 'Category'),
                onSaved: (value) => category = value ?? '',
                validator: (value) => (value == null || value.isEmpty)
                    ? 'Please enter a category'
                    : null,
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _submit,
                child: Text('Submit'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
